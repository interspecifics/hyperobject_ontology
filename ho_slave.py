import json
import os
import pygame
from ffpyplayer.player import MediaPlayer
from oscpy.server import OSCThreadServer
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

class SlavePlayer:
    def __init__(self, orientation):
        print("\n=== Slave Player Initialization ===")
        self.orientation = orientation
        self.current_video = None
        self.player = None
        self.stop_event = Event()
        self.frame_queue = Queue(maxsize=4)
        self.video_queue = Queue()
        self.video_finished = Event()
        
        # Filter videos for this orientation
        self.available_videos = {
            video['name']: video for video in videos 
            if video['orientation'].lower() == orientation
        }
        
        print(f"\nFound {len(self.available_videos)} videos for {orientation} orientation")
        
        # Initialize pygame display
        pygame.init()
        if orientation == "hor":
            self.screen = pygame.display.set_mode(
                (1920, 1080),
                pygame.FULLSCREEN | pygame.NOFRAME
            )
        else:
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
        
        print(f"Display initialized: {self.screen.get_width()}x{self.screen.get_height()}")

    def main_loop(self):
        """Main video playback loop"""
        clock = pygame.time.Clock()
        
        while True:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            # If current video is finished, check for next video
            if self.video_finished.is_set():
                self.video_finished.clear()
                self.screen.blit(self.black_surface, (0, 0))
                pygame.display.flip()

            # Check for new video when no video is playing
            if self.current_video is None:
                try:
                    video_name = self.video_queue.get_nowait()
                    self._start_video(video_name)
                except Queue.Empty:
                    pass
                
            # Display frames if available
            try:
                frame_data = self.frame_queue.get_nowait()
                if frame_data == "EOF":
                    self.stop_video()
                    self.video_finished.set()
                elif isinstance(frame_data, pygame.Surface):
                    self.screen.blit(frame_data, (0, 0))
                    pygame.display.flip()
            except Queue.Empty:
                pass
                
            # Use video-specific FPS if available
            fps = self.current_video.get('fps', 30) if self.current_video else 30
            clock.tick(fps)

    def _start_video(self, video_name):
        """Start playing a video"""
        if video_name not in self.available_videos:
            print(f"Video not found: {video_name}")
            return

        print(f"\nStarting video: {video_name}")
        
        # Clean up previous video
        if self.player:
            self.stop_video()
            
        try:
            self.current_video = self.available_videos[video_name]
            self.stop_event.clear()
            self.video_finished.clear()
            self.player = MediaPlayer(self.current_video['path'])
            
            # Start frame fetching thread
            fetch_thread = Thread(target=self._fetch_frames)
            fetch_thread.daemon = True
            fetch_thread.start()
            
        except Exception as e:
            print(f"Error starting video: {e}")
            self.stop_video()

    def _fetch_frames(self):
        """Fetch and convert frames in separate thread"""
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

    def stop_video(self):
        """Stop the current video"""
        self.stop_event.set()
        if self.player:
            self.player.close_player()
            self.player = None
        self.current_video = None

class SlaveNode:
    def __init__(self, orientation, node):
        print(f"Initializing slave node {node} with orientation {orientation}")
        self.orientation = orientation
        self.node = node
        
        # Initialize video player
        self.player = SlavePlayer(orientation)
        
        # Initialize OSC server
        self.osc_server = OSCThreadServer()
        port = self._get_port(orientation, node)
        
        try:
            self.sock = self.osc_server.listen(
                address='0.0.0.0',
                port=port,
                default=True
            )
            print(f"Listening on port {port}")
        except Exception as e:
            print(f"Error binding OSC server: {e}")
            raise
        
        # Register OSC handlers
        self.osc_server.bind(b'/play', self.handle_play)
        self.osc_server.bind(b'/stop', self.handle_stop)

    def _get_port(self, orientation, node):
        """Get the correct port based on orientation and node number"""
        if orientation == "hor":
            return 8001 if node == 1 else 8002
        else:
            return 8003 if node == 1 else 8004

    def handle_play(self, video_name):
        """Handle incoming play command"""
        video_name = video_name.decode()
        print(f"Received play command for: {video_name}")
        self.player.video_queue.put(video_name)

    def handle_stop(self):
        """Handle stop command"""
        print("Received stop command")
        self.player.stop_video()

    def run(self):
        """Main loop"""
        try:
            self.player.main_loop()
        except KeyboardInterrupt:
            print("Shutting down...")
        except Exception as e:
            print(f"Error in main loop: {e}")
            raise
        finally:
            pygame.quit()

def main():
    parser = argparse.ArgumentParser(description='Video Player Slave Node')
    parser.add_argument('--orientation', required=True, choices=['hor', 'ver'],
                      help='Display orientation (hor/ver)')
    parser.add_argument('--node', required=True, type=int, choices=[1, 2],
                      help='Node number (1 or 2)')
    args = parser.parse_args()
    
    try:
        slave = SlaveNode(args.orientation, args.node)
        slave.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()