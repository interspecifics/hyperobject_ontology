import json
import pygame
import threading
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import time
import random
from collections import defaultdict

class VideoOrchestrator:
    def __init__(self):
        # Load video metadata
        with open('ontology_map.json', 'r') as f:
            self.videos = json.load(f)
            
        # Initialize OSC server
        self.osc_server = OSCThreadServer()
        self.sock = self.osc_server.listen(address='0.0.0.0', port=7000, default=True)
        
        # Track connected slaves
        self.slaves = {
            'hor': [],  # List of horizontal display slaves
            'ver': []   # List of vertical display slaves
        }
        
        # Register handlers
        self.osc_server.bind(b'/slave/announce', self.handle_slave_announce)
        
        # Create clients dict for slaves
        self.slave_clients = {}
        
    def handle_slave_announce(self, slave_id, orientation):
        slave_id = slave_id.decode()
        orientation = orientation.decode()
        
        print(f"New slave announced: {slave_id} ({orientation})")
        
        if slave_id not in self.slaves[orientation]:
            self.slaves[orientation].append(slave_id)
            # Create client for this slave
            port = 8001 if orientation == "hor" else 8002
            self.slave_clients[slave_id] = OSCClient('192.168.1.'+slave_id.split('-')[0], port)

    def organize_videos_by_type(self, category, orientation):
        """Split videos into animated and text types for a given category and orientation"""
        category_videos = [v for v in self.videos 
                         if v['category'] == category and v['orientation'] == orientation]
        
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
        
        # Calculate number of slots needed
        total_slots = max(
            len(hor_animated) // 2 + len(hor_text),
            len(ver_animated) // 2 + len(ver_text)
        )
        
        # Initialize playlists for each node
        playlists = {
            'hor': [[] for _ in range(2)],  # 2 horizontal nodes
            'ver': [[] for _ in range(2)]   # 2 vertical nodes
        }
        
        # Distribute animated videos
        for i, video in enumerate(hor_animated):
            node_idx = i % 2
            playlists['hor'][node_idx].append(video)
            
        for i, video in enumerate(ver_animated):
            node_idx = i % 2
            playlists['ver'][node_idx].append(video)
        
        # Insert text videos at coordinated positions
        text_interval = max(3, total_slots // (len(hor_text) + len(ver_text)))
        current_pos = text_interval
        
        for text_video in hor_text:
            if current_pos < len(playlists['hor'][0]):
                playlists['hor'][0].insert(current_pos, text_video)
                playlists['hor'][1].insert(current_pos, None)  # Other node waits
                current_pos += text_interval
                
        current_pos = text_interval + text_interval // 2  # Offset for vertical nodes
        for text_video in ver_text:
            if current_pos < len(playlists['ver'][0]):
                playlists['ver'][0].insert(current_pos, text_video)
                playlists['ver'][1].insert(current_pos, None)  # Other node waits
                current_pos += text_interval
        
        return playlists

    def play_category(self, category):
        """Orchestrate playing videos from a category across all slaves"""
        playlists = self.create_synchronized_playlist(category)
        
        # Send playlists to each slave
        for orientation in ['hor', 'ver']:
            for slave_idx, slave_id in enumerate(self.slaves[orientation]):
                playlist = playlists[orientation][slave_idx]
                for video in playlist:
                    if video is not None:  # Skip None entries (wait slots)
                        self.slave_clients[slave_id].send_message(
                            b'/play',
                            [video['name'].encode()]
                        )
                        # Wait for video duration
                        time.sleep(video['duration'])
                    else:
                        # Wait for average video duration when None
                        time.sleep(10)  # Default wait time

    def run(self):
        """Main loop to orchestrate video playback"""
        categories = list(set(v['category'] for v in self.videos))
        
        try:
            while True:
                # Wait for slaves to connect
                if not (self.slaves['hor'] and self.slaves['ver']):
                    print("Waiting for slaves to connect...")
                    time.sleep(5)
                    continue
                
                # Play through categories
                for category in categories:
                    print(f"Playing category: {category}")
                    self.play_category(category)
                    # Wait for longest video duration in category
                    max_duration = max(
                        v['duration'] for v in self.videos 
                        if v['category'] == category
                    )
                    time.sleep(max_duration)
                    
        except KeyboardInterrupt:
            print("Shutting down orchestrator...")

def main():
    orchestrator = VideoOrchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()