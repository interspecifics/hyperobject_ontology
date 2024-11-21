import socket
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

# Load metadata
with open('ontology_map.json', 'r') as f:
    videos = json.load(f)

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
    base = 201 if orientation == "hor" else 203
    return f"192.168.1.{base + node - 1}"

class VideoPlayer:
    def __init__(self, orientation, slave_id):
        self.orientation = orientation
        self.slave_id = slave_id
        self.current_video = None
        self.player = None
        self.screen = None
        self.stop_event = Event()
        
        # Filter videos by orientation
        self.available_videos = {
            video['name']: video for video in videos 
            if video['orientation'].lower() == self.orientation
        }
        
        # Initialize pygame
        pygame.init()
        
        # Set up display based on orientation
        if orientation == "hor":
            self.screen = pygame.display.set_mode((1280, 768), pygame.FULLSCREEN)
        else:  # vertical
            self.screen = pygame.display.set_mode((768, 1280), pygame.FULLSCREEN)
            
        pygame.display.set_caption(f'Video Player - {orientation} - {slave_id}')

    def play_video(self, video_name):
        """Play a single video and return when complete"""
        if video_name not in self.available_videos:
            print(f"Video not found: {video_name}")
            return

        video = self.available_videos[video_name]
        
        if self.player:
            self.player.close_player()
            
        self.stop_event.clear()
        self.player = MediaPlayer(video['path'])
        clock = pygame.time.Clock()

        while not self.stop_event.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_event.set()
                    return

            frame, val = self.player.get_frame()
            
            if val == 'eof':
                break
                
            if frame is not None:
                image, pts = frame
                
                # Convert frame to pygame surface
                surface = pygame.image.frombuffer(
                    image.to_bytearray()[0],
                    image.get_size(),
                    "RGB"
                )
                
                # Scale to fit screen while maintaining aspect ratio
                screen_rect = self.screen.get_rect()
                surface = pygame.transform.scale(surface, screen_rect.size)
                
                self.screen.blit(surface, (0, 0))
                pygame.display.flip()
                clock.tick(30)

        if self.player:
            self.player.close_player()
            self.player = None

    def stop_video(self):
        """Stop the current video playback"""
        self.stop_event.set()

class SlaveNode:
    def __init__(self, orientation, ip_address):
        self.slave_id = str(uuid.uuid4())
        self.orientation = orientation
        self.osc_server = OSCThreadServer()
        self.video_player = VideoPlayer(orientation, self.slave_id)
        self.video_queue = Queue()
        self.current_video = None
        
        # Bind OSC server
        self.sock = self.osc_server.listen(
            address='0.0.0.0',
            port=8000 + (1 if orientation == "hor" else 2),
            default=True
        )
        
        # Register OSC handlers
        self.osc_server.bind(b'/play', self.handle_play)
        self.osc_server.bind(b'/stop', self.handle_stop)
        
        # Create client to respond to master
        self.client = OSCClient('192.168.1.200', 7000)
        
        # Start video player thread
        self.player_thread = Thread(target=self.video_player_loop)
        self.player_thread.daemon = True
        self.player_thread.start()
        
        # Announce presence to master
        self.client.send_message(
            b'/slave/announce',
            [self.slave_id.encode(), orientation.encode()]
        )

    def handle_play(self, video_name):
        """Handle incoming play command"""
        video_name = video_name.decode()
        print(f"Received play command for: {video_name}")
        self.video_queue.put(video_name)

    def handle_stop(self):
        """Handle stop command"""
        if self.video_player:
            self.video_player.stop_video()

    def video_player_loop(self):
        """Main loop for video playback"""
        while True:
            video_name = self.video_queue.get()
            self.current_video = video_name
            self.video_player.play_video(video_name)
            self.current_video = None

def main():
    args = parse_arguments()
    ip_address = args.ip or get_default_ip(args.orientation, args.node)
    
    # Initialize slave node with command line arguments
    slave = SlaveNode(args.orientation, ip_address)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down slave node...")
        if slave.video_player:
            slave.video_player.stop_video()
        pygame.quit()

if __name__ == "__main__":
    main()