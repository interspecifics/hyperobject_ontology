import socket
import json
import os
import pygame
from ffpyplayer.player import MediaPlayer
import uuid
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import time

# Load metadata
with open('ontology_map.json', 'r') as f:
    videos = json.load(f)

class VideoPlayer:
    def __init__(self, orientation, slave_id):
        self.orientation = orientation  # "hor" or "ver"
        self.slave_id = slave_id
        self.current_video = None
        self.player = None
        self.screen = None
        
        # Filter videos by orientation
        self.available_videos = [
            video for video in videos 
            if video['orientation'].lower() == self.orientation
        ]
        
        # Initialize pygame
        pygame.init()
        
        # Set up display based on orientation
        if orientation == "hor":
            self.screen = pygame.display.set_mode((1280, 768))
        else:  # vertical
            self.screen = pygame.display.set_mode((768, 1280))
            
        pygame.display.set_caption(f'Video Player - {orientation} - {slave_id}')

    def play_video(self, video_path):
        if self.player:
            self.player.close_player()
            
        self.player = MediaPlayer(video_path)
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.player.close_player()
                    return

            frame, val = player.get_frame()
            if val == 'eof':
                break
                
            if frame is not None:
                img, t = frame
                img = pygame.image.frombuffer(img.to_bytearray()[0], img.get_size(), "RGB")
                self.screen.blit(img, (0, 0))
                pygame.display.flip()
                clock.tick(30)

class SlaveNode:
    def __init__(self, orientation):
        self.slave_id = str(uuid.uuid4())
        self.orientation = orientation
        self.osc_server = OSCThreadServer()
        self.video_player = VideoPlayer(orientation, self.slave_id)
        
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
        self.client = OSCClient('192.168.1.100', 7000)
        
        # Announce presence to master
        self.client.send_message(
            b'/slave/announce',
            [self.slave_id.encode(), orientation.encode()]
        )

    def handle_play(self, video_name):
        video_to_play = next(
            (v for v in self.video_player.available_videos 
             if v['name'] == video_name.decode()),
            None
        )
        
        if video_to_play:
            self.video_player.play_video(video_to_play['path'])
            
    def handle_stop(self):
        if self.video_player.player:
            self.video_player.player.close_player()

def main():
    # Determine orientation based on hostname
    hostname = socket.gethostname()
    orientation = "hor" if "horizontal" in hostname.lower() else "ver"
    
    slave = SlaveNode(orientation)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down slave node...")

if __name__ == "__main__":
    main()