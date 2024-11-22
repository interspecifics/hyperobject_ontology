import json
import pygame
import threading
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import time
import random
from collections import defaultdict
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/video_player/logs/master.log'),
        logging.StreamHandler()
    ]
)

def get_slave_port(orientation, node):
    """Get the correct port based on orientation and node number"""
    if orientation == "hor":
        return 8001 if node == 1 else 8002  # hor1: 8001, hor2: 8002
    else:
        return 8003 if node == 1 else 8004  # ver1: 8003, ver2: 8004

def get_absolute_video_path(relative_path):
    """Convert relative video path to absolute path"""
    base_dir = '/home/pi/video_player'
    return os.path.join(base_dir, relative_path)

class VideoOrchestrator:
    def __init__(self):
        logging.info("Initializing Video Orchestrator")
        
        # Load video metadata
        try:
            with open('/home/pi/video_player/ontology_map.json', 'r') as f:
                self.videos = json.load(f)
                # Convert all video paths
                for video in self.videos:
                    video['path'] = get_absolute_video_path(video['path'])
            logging.info("Loaded video metadata successfully")
        except Exception as e:
            logging.error(f"Failed to load video metadata: {e}")
            raise
            
        # Initialize OSC server
        try:
            self.osc_server = OSCThreadServer()
            self.sock = self.osc_server.listen(
                address='0.0.0.0',
                port=7000,
                default=True
            )
            logging.info("OSC server listening on port 7000")
        except Exception as e:
            logging.error(f"Error initializing OSC server: {e}")
            raise

        # Add a running flag
        self.running = True
        
        # Track connected slaves
        self.slaves = {
            'hor': [],  # List of horizontal display slaves
            'ver': []   # List of vertical display slaves
        }
        
        # Register handlers
        self.osc_server.bind(b'/slave/announce', self.handle_slave_announce)
        
        # Create clients dict for slaves
        self.slave_clients = {}
        
        logging.info("Video Orchestrator initialized")

    def handle_slave_announce(self, slave_id, orientation):
        """Handle slave node announcements"""
        try:
            slave_id = slave_id.decode()
            orientation = orientation.decode()
            logging.info(f"Slave announced: {slave_id} ({orientation})")
            
            if slave_id not in self.slaves[orientation]:
                self.slaves[orientation].append(slave_id)
                # Create client for this slave using its ID to determine IP and port
                ip = f"192.168.1.{slave_id}"
                # Determine if this is node 1 or 2 based on IP
                node = 1 if slave_id in ['201', '203'] else 2
                port = get_slave_port(orientation, node)
                self.slave_clients[slave_id] = OSCClient(ip, port)
                logging.info(f"Created client for slave at {ip}:{port}")
                logging.info(f"Current slaves: hor={self.slaves['hor']}, ver={self.slaves['ver']}")
        except Exception as e:
            logging.error(f"Error in handle_slave_announce: {e}", exc_info=True)
            raise

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
            while self.running:  # Use running flag instead of True
                # Wait for slaves to connect
                if not (self.slaves['hor'] and self.slaves['ver']):
                    logging.info("Waiting for slaves to connect...")
                    time.sleep(5)
                    continue
                
                # Play through categories
                for category in categories:
                    logging.info(f"Playing category: {category}")
                    self.play_category(category)
                    # Wait for longest video duration in category
                    max_duration = max(
                        v['duration'] for v in self.videos 
                        if v['category'] == category
                    )
                    time.sleep(max_duration)
                    
        except KeyboardInterrupt:
            logging.info("Shutting down orchestrator...")
            self.running = False
        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)
            self.running = False

def main():
    try:
        orchestrator = VideoOrchestrator()
        logging.info("Starting Video Orchestrator")
        orchestrator.run()
    except KeyboardInterrupt:
        logging.info("Shutting down orchestrator...")
    except Exception as e:
        logging.error(f"Error in main: {e}", exc_info=True)

if __name__ == "__main__":
    # Ensure log directory exists
    os.makedirs('/home/pi/video_player/logs', exist_ok=True)
    main()