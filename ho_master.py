import socket
import json
import pygame
import threading


# Initialize pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((640, 480)) # 1920x1080

# Function to play video
def play_video(video_name):
    # Load and play the video using pygame
    movie = pygame.movie.Movie(video_name)
    movie_screen = pygame.Surface(movie.get_size()).convert()
    movie.set_display(movie_screen)
    movie.play()

    while movie.get_busy():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                movie.stop()
                pygame.quit()
                return
        screen.blit(movie_screen, (0, 0))
        pygame.display.update()

# Function for slave to receive tags
def slave_receive_tags(slave_id, host='0.0.0.0', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port + slave_id))
        s.listen()
        print(f"Slave {slave_id} listening on port {port + slave_id}")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    message = json.loads(data.decode('utf-8'))
                    video_name = message['video_name']
                    tags = message['tags']
                    print(f"Slave {slave_id} received tags: {tags}")
                    # Load and play the video based on the received message
                    play_video(video_name)

# Start slave threads
for i in range(3):
    threading.Thread(target=slave_receive_tags, args=(i,)).start()

# Set up the server to listen for messages from the master
host = '0.0.0.0'
port = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()

    while True:
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024)
            if data:
                message = json.loads(data.decode('utf-8'))
                video_name = message['video_name']
                tags = message['tags']
                # Load and play the video based on the received message
                play_video(video_name)