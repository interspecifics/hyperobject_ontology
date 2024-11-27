import json
import os
import vlc
import time
import random
import argparse

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
        
        # Basic VLC initialization with minimal options
        vlc_args = [
            '--no-audio',                # Disable audio
            '--fullscreen',              # Force fullscreen
            '--no-video-title-show',     # Don't show title
            '--no-osd',                  # No on-screen display
            '--quiet'                    # Minimal logging
        ]
        
        self.instance = vlc.Instance(' '.join(vlc_args))  # Join args with spaces
        
        # Create two players for seamless transitions
        self.player_a = self.instance.media_player_new()
        self.player_b = self.instance.media_player_new()
        self.current_player = self.player_a
        self.next_player = self.player_b
        
        # Set both players to fullscreen
        self.player_a.set_fullscreen(True)
        self.player_b.set_fullscreen(True)
        
        # Hide cursor
        os.system('setterm -cursor off')
        
        # Get unique categories
        self.categories = sorted(set(video['category'] for video in videos))
        print(f"\nFound {len(self.categories)} categories: {self.categories}")

    def _switch_players(self):
        """Switch current and next players"""
        self.current_player, self.next_player = self.next_player, self.current_player

    def _play_video(self, video):
        """Play a single video"""
        print(f"\nPlaying: {video['name']} ({video['fps']} FPS)")
        
        try:
            # Prepare next video
            media = self.instance.media_new(video['path'])
            self.next_player.set_media(media)
            
            # Start next video
            self.next_player.play()
            
            # Wait for video to actually start
            while self.next_player.get_state() not in [vlc.State.Playing, vlc.State.Ended, vlc.State.Error]:
                time.sleep(0.05)
            
            if self.next_player.get_state() == vlc.State.Error:
                print("Error starting video")
                return
            
            # Stop current video (if any)
            self.current_player.stop()
            
            # Switch players
            self._switch_players()
            
            # Wait for exact duration
            time.sleep(video['duration'])
            
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
        
        while True:
            print(f"\n=== Starting playback with seed {self.current_seed} ===")
            
            for category in self.categories:
                print(f"\n=== Playing Category: {category} ===")
                playlist = self.prepare_category_playlist(category)
                
                for video in playlist:
                    self._play_video(video)
            
            self.current_seed += 1
            print(f"\n=== Completed seed {self.current_seed-1}, moving to seed {self.current_seed} ===")

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

if __name__ == "__main__":
    main() 