import json
import os
import pygame
from ffpyplayer.player import MediaPlayer
import random
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

class OfflinePlayer:
    def __init__(self, device_name):
        print(f"\n=== Offline Player Initialization for {device_name} ===")
        
        # Parse device name to get orientation and node number
        self.orientation = device_name[:3]  # 'hor' or 'ver'
        self.node_number = int(device_name[3])  # 1 or 2
        self.current_seed = 1
        
        print(f"Orientation: {self.orientation}, Node: {self.node_number}")
        
        self.current_video = None
        self.player = None
        self.stop_event = Event()
        self.frame_queue = Queue(maxsize=4)
        self.video_finished = Event()
        
        # Get unique categories in alphabetical order
        self.categories = sorted(set(video['category'] for video in videos))
        print(f"\nFound {len(self.categories)} categories: {self.categories}")
        
        # Initialize pygame display
        pygame.init()
        if self.orientation == "hor":
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
        self.black_surface = pygame.Surface(self.screen.get_rect().size)
        self.black_surface.fill((0, 0, 0))
        
        print(f"Display initialized: {self.screen.get_width()}x{self.screen.get_height()}")

    def prepare_category_playlist(self, category):
        """Prepare a playlist for a category using deterministic shuffling"""
        # Set random seed for deterministic shuffling
        random.seed(self.current_seed)
        
        # Filter videos for this category and orientation
        category_videos = [v for v in videos if v['category'] == category and v['orientation'].lower() == self.orientation]
        
        # Separate animated and text videos
        animated_videos = [v for v in category_videos if v['video_type'] == 'animated']
        text_videos = [v for v in category_videos if v['video_type'] == 'text']
        
        # Shuffle both lists with current seed
        random.shuffle(animated_videos)
        random.shuffle(text_videos)
        
        # Create playlist alternating between animated and text
        playlist = []
        text_index = 0
        
        for i, animated in enumerate(animated_videos):
            playlist.append(animated)
            if i % 3 == 1 and text_index < len(text_videos):
                playlist.append(text_videos[text_index])
                text_index += 1
        
        # Filter playlist based on node number (1: even indices, 2: odd indices)
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
        
        while True:  # Loop through seeds
            print(f"\n=== Starting playback with seed {self.current_seed} ===")
            
            for category in self.categories:
                print(f"\n=== Playing Category: {category} ===")
                playlist = self.prepare_category_playlist(category)
                
                for video in playlist:
                    self._play_video(video)
            
            # Move to next seed after completing all categories
            self.current_seed += 1
            print(f"\n=== Completed seed {self.current_seed-1}, moving to seed {self.current_seed} ===")

    def _play_video(self, video):
        """Play a single video"""
        print(f"\nPlaying: {video['name']} (Type: {video['video_type']})")
        
        try:
            self.current_video = video
            self.player = MediaPlayer(video['path'])
            self.stop_event.clear()
            
            # Start frame fetching thread
            fetch_thread = Thread(target=self._fetch_frames)
            fetch_thread.daemon = True
            fetch_thread.start()
            
            # Main display loop for this video
            clock = pygame.time.Clock()
            while not self.stop_event.is_set():
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                
                try:
                    frame_data = self.frame_queue.get(timeout=0.1)
                    if frame_data == "EOF":
                        break
                    elif isinstance(frame_data, pygame.Surface):
                        self.screen.blit(frame_data, (0, 0))
                        pygame.display.flip()
                except Queue.Empty:
                    pass
                
                clock.tick(video.get('fps', 30))
            
            # Clean up
            if self.player:
                self.player.close_player()
                self.player = None
            
            # Show black screen between videos
            self.screen.blit(self.black_surface, (0, 0))
            pygame.display.flip()
            
            return True
            
        except Exception as e:
            print(f"Error playing video: {e}")
            return True

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

def main():
    parser = argparse.ArgumentParser(description='Offline Video Player')
    parser.add_argument('--device', required=True, choices=['hor1', 'hor2', 'ver1', 'ver2'],
                      help='Device name (hor1/hor2/ver1/ver2)')
    args = parser.parse_args()
    
    try:
        player = OfflinePlayer(args.device)
        player.run_player()
    except KeyboardInterrupt:
        print("\nPlayback terminated by user")
    except Exception as e:
        print(f"\nError in playback: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main() 