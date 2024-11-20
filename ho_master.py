import json
import pygame
import threading
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import time
import random

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

    def select_videos_by_category(self, category):
        """Select videos for all displays in a category"""
        hor_videos = [v for v in self.videos if v['category'] == category and v['orientation'] == 'hor']
        ver_videos = [v for v in self.videos if v['category'] == category and v['orientation'] == 'ver']
        
        selected = {
            'hor': random.sample(hor_videos, min(len(hor_videos), len(self.slaves['hor']))),
            'ver': random.sample(ver_videos, min(len(ver_videos), len(self.slaves['ver'])))
        }
        
        return selected

    def play_category(self, category):
        """Orchestrate playing videos from a category across all slaves"""
        videos = self.select_videos_by_category(category)
        
        # Send videos to horizontal displays
        for slave_id, video in zip(self.slaves['hor'], videos['hor']):
            self.slave_clients[slave_id].send_message(
                b'/play',
                [video['name'].encode()]
            )
            
        # Send videos to vertical displays
        for slave_id, video in zip(self.slaves['ver'], videos['ver']):
            self.slave_clients[slave_id].send_message(
                b'/play',
                [video['name'].encode()]
            )

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