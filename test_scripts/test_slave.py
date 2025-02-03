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

class TestPlayer:
    def __init__(self, orientation):
        print("\n=== Test Player Initialization ===")
        self.orientation = orientation
        self.current_video = None
        self.player = None
        self.stop_event = Event()
        self.frame_queue = Queue(maxsize=4)
        self.command_queue = Queue()
        self.video_finished = Event()
        
        # Get unique categories in alphabetical order
        self.categories = sorted(set(video['category'] for video in videos))
        print(f"\nFound {len(self.categories)} categories: {self.categories}")
        
        # Initialize pygame display
        pygame.init()
        if orientation == "hor":
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

    def prepare_category_playlist(self, category):
        """Prepare a playlist for a category that alternates between animated and text videos"""
        # Filter videos for this category and orientation
        category_videos = [v for v in videos if v['category'] == category and v['orientation'].lower() == self.orientation]
        
        # Separate animated and text videos
        animated_videos = [v for v in category_videos if v['video_type'] == 'animated']
        text_videos = [v for v in category_videos if v['video_type'] == 'text']
        
        # Shuffle both lists
        random.shuffle(animated_videos)
        random.shuffle(text_videos)
        
        # Create playlist alternating between animated and text
        playlist = []
        text_index = 0
        
        for i, animated in enumerate(animated_videos):
            playlist.append(animated)
            # Insert a text video after every 2-3 animated videos
            if i % 3 == 1 and text_index < len(text_videos):  # Adjust this number to change frequency
                playlist.append(text_videos[text_index])
                text_index += 1
        
        return playlist

    def run_test(self):
        """Play videos from all categories"""
        print("\n=== Starting Video Test Sequence ===")
        
        for category in self.categories:
            print(f"\n=== Testing Category: {category} ===")
            playlist = self.prepare_category_playlist(category)
            
            print(f"Prepared playlist with {len(playlist)} videos")
            for video in playlist:
                print(f"\nPlaying: {video['name']}")
                print(f"Type: {video['video_type']}")
                
                try:
                    self.current_video = video
                    self.player = MediaPlayer(video['path'])
                    
                    # Start frame fetching thread
                    fetch_thread = Thread(target=self._fetch_frames)
                    fetch_thread.daemon = True
                    fetch_thread.start()
                    
                    # Main display loop for this video
                    clock = pygame.time.Clock()
                    while not self.stop_event.is_set():
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                return
                        
                        try:
                            frame_data = self.frame_queue.get(timeout=0.1)
                            if frame_data == "EOF":
                                break
                            elif isinstance(frame_data, pygame.Surface):
                                self.screen.blit(frame_data, (0, 0))
                                pygame.display.flip()
                        except:
                            pass
                        
                        clock.tick(video.get('fps', 30))
                    
                    # Clean up before next video
                    self.stop_event.set()
                    if self.player:
                        self.player.close_player()
                        self.player = None
                    self.stop_event.clear()
                    
                    # Show black screen between videos
                    self.screen.blit(self.black_surface, (0, 0))
                    pygame.display.flip()
                    
                except Exception as e:
                    print(f"Error playing video: {e}")
                    continue

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
    parser = argparse.ArgumentParser(description='Test Video Player')
    parser.add_argument('--orientation', required=True, choices=['hor', 'ver'],
                      help='Display orientation (hor/ver)')
    args = parser.parse_args()
    
    try:
        player = TestPlayer(args.orientation)
        player.run_test()
    except KeyboardInterrupt:
        print("\nTest terminated by user")
    except Exception as e:
        print(f"\nError in test: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main() 