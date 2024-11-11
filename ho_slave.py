import socket
import json
import os
import pygame
from ffpyplayer.player import MediaPlayer
import uuid  # Import uuid for generating unique IDs

# Load metadata
with open('videos.json', 'r') as f:
    videos = json.load(f)

# Create a unique ID for this slave
slave_id = str(uuid.uuid4())

# Create a socket server to listen for the master's message
host = '0.0.0.0'
port = 12345

def play_video(video_path):
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Video Player')

    player = MediaPlayer(video_path)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                player.close_player()
                pygame.quit()
                return

        frame, val = player.get_frame()
        if val == 'eof':
            break
        if frame is not None:
            img, t = frame
            img = pygame.image.frombuffer(img.to_bytearray()[0], img.get_size(), "RGB")
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(30)

    player.close_player()
    pygame.quit()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()

    print("Waiting for connection from master...")
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        # Send the slave ID to the master
        conn.sendall(slave_id.encode('utf-8'))
        data = conn.recv(1024).decode('utf-8')
        if data:
            # Find the video in the metadata
            video_to_play = next((video for video in videos if video['name'] == data), None)
            if video_to_play:
                print(f"Loading video: {video_to_play['name']}")
                video_path = f"{video_to_play['name']}.mp4"
                play_video(video_path)