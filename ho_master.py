import json
import os
import time
from oscpy.client import OSCClient
import random
import subprocess
import argparse
from queue import Queue, Empty
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

class MasterNode:
    def __init__(self, local_slave):
        print("\n=== Master Node Initialization ===")
        self.local_slave = local_slave  # 'hor1', 'ver1', etc.
        
        # Get unique categories in alphabetical order
        self.categories = sorted(set(video['category'] for video in videos))
        print(f"\nFound {len(self.categories)} categories: {self.categories}")
        
        # Initialize OSC clients for each slave
        self.slaves = {
            'hor1': OSCClient('127.0.0.1' if local_slave == 'hor1' else '192.168.1.201', 8001),
            'hor2': OSCClient('192.168.1.202', 8002),
            'ver1': OSCClient('127.0.0.1' if local_slave == 'ver1' else '192.168.1.203', 8003),
            'ver2': OSCClient('192.168.1.204', 8004)
        }
        
        print("\nInitialized OSC clients:")
        for slave, client in self.slaves.items():
            print(f"  {slave}: {client._address}:{client._port}")

    def organize_videos_by_type(self, category, orientation):
        """Separate videos by type for a given category and orientation"""
        category_videos = [v for v in videos 
                         if v['category'] == category 
                         and v['orientation'].lower() == orientation]
        
        animated = [v for v in category_videos if v['video_type'] == 'animated']
        text = [v for v in category_videos if v['video_type'] == 'text']
        
        return animated, text

    def create_synchronized_playlist(self, category):
        """Create synchronized playlists for all nodes for a given category"""
        # Get videos for each orientation
        hor_animated, hor_text = self.organize_videos_by_type(category, 'hor')
        ver_animated, ver_text = self.organize_videos_by_type(category, 'ver')
        
        # Shuffle all video lists
        random.shuffle(hor_animated)
        random.shuffle(hor_text)
        random.shuffle(ver_animated)
        random.shuffle(ver_text)
        
        # Initialize playlists
        playlists = {
            'hor1': [], 'hor2': [],
            'ver1': [], 'ver2': []
        }
        
        # Distribute animated videos between node pairs
        for i, video in enumerate(hor_animated):
            node = 'hor1' if i % 2 == 0 else 'hor2'
            playlists[node].append(video)
            
        for i, video in enumerate(ver_animated):
            node = 'ver1' if i % 2 == 0 else 'ver2'
            playlists[node].append(video)
        
        # Insert text videos at intervals (never simultaneously)
        text_interval = 3  # Show text video after every 3 animated videos
        
        # Add text videos to horizontal nodes
        for i, text_video in enumerate(hor_text):
            pos = (i + 1) * text_interval
            if pos < len(playlists['hor1']):
                playlists['hor1'].insert(pos, text_video)
                playlists['hor2'].insert(pos, None)  # Other node waits
        
        # Add text videos to vertical nodes (offset from horizontal)
        for i, text_video in enumerate(ver_text):
            pos = (i + 1) * text_interval + 2  # Offset to avoid simultaneous text videos
            if pos < len(playlists['ver1']):
                playlists['ver1'].insert(pos, text_video)
                playlists['ver2'].insert(pos, None)  # Other node waits
        
        return playlists

    def play_video(self, node, video):
        """Send play command to a specific node"""
        if video is None:
            return
        try:
            self.slaves[node].send_message(b'/play', [video['name'].encode()])
            print(f"Sent play command to {node}: {video['name']}")
        except Exception as e:
            print(f"Error sending play command to {node}: {e}")

    def run(self):
        """Main execution loop"""
        print("\n=== Starting Video Playback ===")
        
        try:
            # Process each category in alphabetical order
            for category in self.categories:
                print(f"\n=== Processing Category: {category} ===")
                
                # Create synchronized playlists for this category
                playlists = self.create_synchronized_playlist(category)
                
                # Get maximum playlist length
                max_length = max(len(playlist) for playlist in playlists.values())
                
                # Play videos from playlists
                for i in range(max_length):
                    for node in ['hor1', 'hor2', 'ver1', 'ver2']:
                        if i < len(playlists[node]):
                            video = playlists[node][i]
                            if video:
                                self.play_video(node, video)
                    
                    # Wait for videos to finish (approximate)
                    # In a real implementation, you might want to add synchronization mechanisms
                    time.sleep(12)  # Adjust based on typical video duration
                
                print(f"Finished category: {category}")
                
        except KeyboardInterrupt:
            print("\nPlayback interrupted by user")
        except Exception as e:
            print(f"\nError during playback: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Video Player Master Node')
    parser.add_argument('--local-slave', required=True, 
                      choices=['hor1', 'ver1'],
                      help='Which slave node runs on this device')
    args = parser.parse_args()
    
    try:
        master = MasterNode(args.local_slave)
        master.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()