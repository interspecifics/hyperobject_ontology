import json
import os
import pygame
from ffpyplayer.player import MediaPlayer
import uuid
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import time
import argparse
from queue import Queue
from threading import Thread, Event
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

def get_absolute_video_path(relative_path):
    """Convert relative video path to absolute path"""
    base_dir = '/home/pi/video_player'
    return os.path.join(base_dir, relative_path)

# Load metadata
with open('/home/pi/video_player/ontology_map.json', 'r') as f:
    videos = json.load(f)
    for video in videos:
        video['path'] = get_absolute_video_path(video['path'])

def parse_arguments():
    parser = argparse.ArgumentParser(description='Video Player Slave Node')
    parser.add_argument('--orientation', required=True, choices=['hor', 'ver'],
                      help='Display orientation (hor/ver)')
    parser.add_argument('--node', required=True, type=int, choices=[1, 2],
                      help='Node number (1 or 2)')
    parser.add_argument('--ip', 
                      help='IP address (optional, will be auto-assigned if not provided)')
    return parser.parse_args()

def get_default_ip(orientation, node):
    """Calculate default IP based on orientation and node number"""
    if orientation == "hor":
        return f"192.168.1.{201 if node == 1 else 202}"  # 201 for hor1, 202 for hor2
    else:  # vertical
        return f"192.168.1.{203 if node == 1 else 204}"  # 203 for ver1, 204 for ver2

def get_slave_port(orientation, node):
    """Get the correct port based on orientation and node number"""
    if orientation == "hor":
        return 8001 if node == 1 else 8002  # hor1: 8001, hor2: 8002
    else:
        return 8003 if node == 1 else 8004  # ver1: 8003, ver2: 8004

class VideoPlayer:
    def __init__(self, orientation):
        print("\n=== Video Player Initialization ===")
        self.orientation = orientation
        self.current_video = None
        self.player = None
        self.stop_event = Event()
        self.frame_queue = Queue(maxsize=4)
        self.command_queue = Queue()
        self.video_finished = Event()
        
        # Filter videos by orientation
        self.available_videos = {
            video['name']: video for video in videos 
            if video['orientation'].lower() == self.orientation
        }
        
        # Print available videos and their paths for debugging
        print(f"\nFound {len(self.available_videos)} videos for {orientation} orientation:")
        for name, video in self.available_videos.items():
            print(f"\nVideo: {name}")
            print(f"  Path: {video['path']}")
            print(f"  Type: {video['video_type']}")
            print(f"  FPS: {video.get('fps', 30)}")
            if os.path.exists(video['path']):
                size = os.path.getsize(video['path']) / (1024 * 1024)
                print(f"  Size: {size:.2f} MB")
                print(f"  Status: File exists")
            else:
                print(f"  Status: FILE NOT FOUND")
        
        print("\n=== End Video Player Initialization ===\n")
        
        # Screen setup will be done in main thread
        self.screen = None
        self.black_surface = None

    def initialize_display(self):
        """Initialize pygame display (must be called from main thread)"""
        pygame.init()
        if self.orientation == "hor":
            self.screen = pygame.display.set_mode(
                (1920, 1080),
                pygame.FULLSCREEN | pygame.NOFRAME
            )
        else:
            # For vertical, try the smaller resolution first
            try:
                self.screen = pygame.display.set_mode(
                    (768, 1280),
                    pygame.FULLSCREEN | pygame.NOFRAME
                )
            except pygame.error:
                print("Failed to set 768x1280, trying 1080x1920...")
                self.screen = pygame.display.set_mode(
                    (1080, 1920),
                    pygame.FULLSCREEN | pygame.NOFRAME
                )
        
        pygame.mouse.set_visible(False)
        
        # Create black surface for transitions
        self.black_surface = pygame.Surface(self.screen.get_rect().size)
        self.black_surface.fill((0, 0, 0))
        
        print(f"\nFinal display size: {self.screen.get_width()}x{self.screen.get_height()}")

    def main_loop(self):
        """Main loop that runs in the main thread"""
        clock = pygame.time.Clock()
        
        while True:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            # If current video is finished, check for next video
            if self.video_finished.is_set():
                self.video_finished.clear()
                try:
                    # Check for next video in queue
                    if not self.command_queue.empty():
                        video_name = self.command_queue.get_nowait()
                        print(f"Starting next video from queue: {video_name}")
                        self._start_video(video_name)
                except Exception as e:
                    print(f"Error starting next video: {e}")

            # Check for new video commands when no video is playing
            if self.current_video is None:
                try:
                    video_name = self.command_queue.get_nowait()
                    print(f"Starting first video: {video_name}")
                    self._start_video(video_name)
                except Exception:
                    pass
                
            # Display frames if available
            try:
                frame_data = self.frame_queue.get_nowait()
                if frame_data == "EOF":
                    print("Reached end of video")
                    # Show black screen after video ends
                    self.screen.blit(self.black_surface, (0, 0))
                    pygame.display.flip()
                    self.stop_video()
                    self.video_finished.set()
                elif isinstance(frame_data, pygame.Surface):
                    self.screen.blit(frame_data, (0, 0))
                    pygame.display.flip()
            except Exception:
                pass
                
            # Use video-specific FPS if available, otherwise default to 30
            if self.current_video and self.current_video in self.available_videos:
                fps = self.available_videos[self.current_video].get('fps', 30)
            else:
                fps = 30
                
            clock.tick(fps)

    def _start_video(self, video_name):
        """Start playing a video (internal method)"""
        if video_name not in self.available_videos:
            print(f"\nERROR: Video not found in available videos: {video_name}")
            print(f"Available videos are: {list(self.available_videos.keys())}")
            return

        print(f"\n=== Starting Video Playback ===")
        print(f"Video name: {video_name}")
        
        # Clean up previous video before starting new one
        if self.player:
            print("Stopping previous video...")
            self.stop_video()
            print("Clearing frame queue...")
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except:
                    pass
            
        video = self.available_videos[video_name]
        print(f"Video details:")
        print(f"  Path: {video['path']}")
        print(f"  Type: {video['video_type']}")
        print(f"  FPS: {video.get('fps', 30)}")
        
        try:
            print("Creating MediaPlayer...")
            self.current_video = video_name
            self.stop_event.clear()
            self.video_finished.clear()
            self.player = MediaPlayer(video['path'])
            print("MediaPlayer created successfully")
            
            # Start frame fetching thread
            print("Starting frame fetch thread...")
            fetch_thread = Thread(target=self._fetch_frames)
            fetch_thread.daemon = True
            fetch_thread.start()
            print("Frame fetch thread started")
            
        except Exception as e:
            print(f"ERROR starting video: {e}")
            import traceback
            traceback.print_exc()
            return

        print("=== Video Playback Started ===\n")

    def _fetch_frames(self):
        """Fetch frames in separate thread"""
        while not self.stop_event.is_set():
            frame, val = self.player.get_frame()
            
            if val == 'eof':
                self.frame_queue.put("EOF")
                break
                
            if frame is not None:
                image, pts = frame
                try:
                    surface = pygame.image.frombuffer(
                        image.to_bytearray()[0],
                        image.get_size(),
                        "RGB"
                    )
                    surface = pygame.transform.scale(surface, self.screen.get_rect().size)
                    self.frame_queue.put(surface)
                except Exception as e:
                    print(f"Error processing frame: {e}")
                    continue

    def play_video(self, video_name):
        """Queue a video for playback"""
        self.command_queue.put(video_name)

    def stop_video(self):
        """Stop the current video"""
        print(f"Stopping video: {self.current_video}")
        self.stop_event.set()
        if self.player:
            self.player.close_player()
            self.player = None
        self.current_video = None

class SlaveNode:
    def __init__(self, orientation, ip_address, node):
        print(f"Initializing slave node with orientation: {orientation} at IP: {ip_address}")
        self.slave_id = ip_address.split('.')[-1]  # Use last octet of IP as ID
        self.orientation = orientation
        self.node = node
        self.osc_server = OSCThreadServer()
        
        # Initialize video player
        self.video_player = VideoPlayer(orientation)
        print("Video player initialized")
        
        # Initialize display in main thread
        self.video_player.initialize_display()
        
        # Get the correct port for this slave
        port = get_slave_port(orientation, node)
        
        # Bind OSC server
        try:
            self.sock = self.osc_server.listen(
                address='0.0.0.0',
                port=port,
                default=True
            )
            print(f"OSC server listening on port {port}")
        except Exception as e:
            print(f"Error binding OSC server: {e}")
            raise
        
        # Register OSC handlers
        self.osc_server.bind(b'/play', self.handle_play)
        self.osc_server.bind(b'/stop', self.handle_stop)
        
        # Create client to respond to master
        try:
            self.client = OSCClient('192.168.1.200', 7000)
            print("Created OSC client to connect to master")
        except Exception as e:
            print(f"Error creating OSC client: {e}")
            raise

        # Announce presence to master
        try:
            print(f"Announcing presence to master with ID: {self.slave_id}")
            self.client.send_message(
                b'/slave/announce',
                [self.slave_id.encode(), orientation.encode()]
            )
            print("Announcement sent to master")
        except Exception as e:
            print(f"Error announcing to master: {e}")
            raise

    def handle_play(self, video_name):
        """Handle incoming play command"""
        video_name = video_name.decode()
        print(f"Received play command for: {video_name}")
        self.video_queue.put(video_name)  # Use queue instead of direct playback

    def handle_stop(self):
        """Handle stop command"""
        print("Received stop command")
        self.video_player.stop_video()

    def run(self):
        """Main loop that runs in the main thread"""
        print("Starting main loop...")
        try:
            # Run the video player's main loop
            while True:
                self.video_player.main_loop()
                time.sleep(0.1)  # Add small sleep to prevent CPU hogging
        except KeyboardInterrupt:
            print("Received keyboard interrupt")
        except Exception as e:
            print(f"Error in main loop: {e}")
            raise
        finally:
            print("Exiting main loop")

def main():
    args = parse_arguments()
    
    # Get IP address
    ip_address = args.ip or get_default_ip(args.orientation, args.node)
    print(f"Using IP address: {ip_address}")
    
    try:
        # Initialize slave node
        slave = SlaveNode(args.orientation, ip_address, args.node)
        print(f"Slave node initialized with orientation {args.orientation} and node {args.node}")
        
        # Run main loop (this will block)
        slave.run()
    except KeyboardInterrupt:
        print("Shutting down slave node...")
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()