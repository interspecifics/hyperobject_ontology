import json
import os
import pygame
from ffpyplayer.player import MediaPlayer
import random
import argparse
import time
from threading import Thread, Event
from queue import Queue, Empty

def get_absolute_video_path(relative_path):
    base_dir = '/home/pi/video_player'
    return os.path.join(base_dir, relative_path)

# Load metadata
with open('/home/pi/video_player/ontology_map.json', 'r') as f:
    videos = json.load(f)
    for video in videos:
        video['path'] = get_absolute_video_path(video['path'])

class OfflinePlayer:
    def __init__(self, device_name):
        print(f"\n=== Offline Player Initialization for {device_name} ===")
        self.orientation = device_name[:3]  # 'hor' or 'ver'
        self.node_number = int(device_name[3])  # 1 or 2
        self.current_seed = 1
        
        # Initialize pygame display
        pygame.init()
        pygame.display.init()
        
        # Get current display info
        info = pygame.display.Info()
        print(f"Current display resolution: {info.current_w}x{info.current_h}")
        
        # Set display mode using current resolution
        self.screen = pygame.display.set_mode(
            (info.current_w, info.current_h),
            pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        
        print(f"Display initialized with size: {self.screen.get_size()}")
        pygame.mouse.set_visible(False)
        
        # Pre-create black background
        self.black_surface = pygame.Surface(self.screen.get_size())
        self.black_surface.fill((0, 0, 0))
        
        # Initialize player with larger queue for smoother playback
        self.current_player = None
        self.current_queue = Queue(maxsize=16)  # Increased buffer size
        self.stop_event = Event()
        
        # Get unique categories
        self.categories = sorted(set(video['category'] for video in videos))
        print(f"\nFound {len(self.categories)} categories: {self.categories}")

    def _fetch_frames(self, player, queue):
        """Fetch frames from player to queue"""
        frame_count = 0
        last_print = time.time()
        
        while not self.stop_event.is_set():
            frame, val = player.get_frame()
            if val == 'eof':
                queue.put("EOF")
                break
            if frame is not None:
                image, pts = frame
                # Get original frame as surface
                surface = pygame.image.frombuffer(
                    image.to_bytearray()[0],
                    image.get_size(),
                    "RGB"
                )
                
                # Only calculate dimensions once per video
                if frame_count == 0:
                    # Get the original video dimensions
                    video_w, video_h = surface.get_size()
                    screen_w, screen_h = self.screen.get_size()
                    
                    # Calculate position to center the frame
                    self.frame_x = (screen_w - video_w) // 2
                    self.frame_y = (screen_h - video_h) // 2
                    
                    # Print dimensions for first frame only
                    print(f"Video size: {video_w}x{video_h}, Screen size: {screen_w}x{screen_h}, Position: ({self.frame_x}, {self.frame_y})")
                
                # Create new frame with black background (reuse surface if possible)
                final = pygame.Surface(self.screen.get_size())
                final.fill((0, 0, 0))
                
                # Blit at pre-calculated position
                final.blit(surface, (self.frame_x, self.frame_y))
                queue.put(final)
                
                frame_count += 1
                if time.time() - last_print >= 5:  # Print FPS every 5 seconds
                    fps = frame_count / (time.time() - last_print)
                    print(f"Current FPS: {fps:.2f}")
                    frame_count = 0
                    last_print = time.time()

    def _play_video(self, video):
        """Play a single video"""
        print(f"\nPlaying: {video['name']}")
        
        try:
            # Clean up previous player if exists
            if self.current_player:
                self.current_player.close_player()
            
            # Start new player with optimized options
            self.current_player = MediaPlayer(video['path'], ff_opts={
                'framedrop': True,  # Allow frame dropping if needed
                'sync': 'audio',    # Sync to audio clock
                'threads': 4        # Use 4 threads for decoding
            })
            
            self.current_queue = Queue(maxsize=16)
            
            # Start frame fetching thread
            fetch_thread = Thread(target=self._fetch_frames, 
                                args=(self.current_player, self.current_queue))
            fetch_thread.daemon = True
            fetch_thread.start()
            
            # Display frames with minimal processing
            clock = pygame.time.Clock()
            while not self.stop_event.is_set():
                try:
                    frame = self.current_queue.get_nowait()
                    if frame == "EOF":
                        break
                    if isinstance(frame, pygame.Surface):
                        self.screen.blit(frame, (0, 0))
                        pygame.display.flip()
                except Empty:
                    clock.tick(60)  # Limit CPU usage when no frames
                
        except Exception as e:
            print(f"Error playing video: {e}")

    def prepare_category_playlist(self, category):
        """Prepare a playlist for a category"""
        random.seed(self.current_seed)
        
        # Filter videos for this category and orientation
        category_videos = [v for v in videos 
                         if v['category'] == category 
                         and v['orientation'] == self.orientation]  # Direct match with 'hor' or 'ver'
        
        print(f"Found {len(category_videos)} videos for {self.orientation} orientation in {category}")
        
        # Separate animated and text videos
        animated = [v for v in category_videos if v['video_type'] == 'animated']
        text = [v for v in category_videos if v['video_type'] == 'text']
        
        print(f"  Animated videos: {len(animated)}")
        print(f"  Text videos: {len(text)}")
        
        # Shuffle both lists
        random.shuffle(animated)
        random.shuffle(text)
        
        # Create playlist alternating between animated and text
        playlist = []
        text_index = 0
        
        for i, animated_video in enumerate(animated):
            playlist.append(animated_video)
            if i % 3 == 1 and text_index < len(text):
                playlist.append(text[text_index])
                text_index += 1
        
        # Filter playlist based on node number
        filtered_playlist = [
            video for i, video in enumerate(playlist)
            if (i % 2 == 0 and self.node_number == 1) or
               (i % 2 == 1 and self.node_number == 2)
        ]
        
        print(f"Created playlist with {len(filtered_playlist)} videos for node {self.node_number}")
        return filtered_playlist

    def run_player(self):
        """Main playback loop"""
        print("\n=== Starting Offline Playback ===")
        
        try:
            while True:
                print(f"\n=== Starting playback with seed {self.current_seed} ===")
                
                for category in self.categories:
                    print(f"\n=== Playing Category: {category} ===")
                    playlist = self.prepare_category_playlist(category)
                    
                    for video in playlist:
                        self._play_video(video)
                
                self.current_seed += 1
                print(f"\n=== Completed seed {self.current_seed-1}, moving to seed {self.current_seed} ===")
                
        except KeyboardInterrupt:
            self.stop_event.set()
            if self.current_player:
                self.current_player.close_player()
            pygame.quit()

def main():
    parser = argparse.ArgumentParser(description='Offline Video Player')
    parser.add_argument('--device', required=True, choices=['hor1', 'hor2', 'ver1', 'ver2'],
                      help='Device name (hor1/hor2/ver1/ver2)')
    
    args = parser.parse_args()
    
    try:
        player = OfflinePlayer(args.device)
        player.run_player()
    except Exception as e:
        print(f"\nError in playback: {e}")
        pygame.quit()

if __name__ == "__main__":
    main() 