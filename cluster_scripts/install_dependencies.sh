#!/bin/bash

# Update package list
sudo apt-get update

# Install required system packages
sudo apt-get install -y \
    python3-pip \
    python3-pygame \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev

# Install required Python packages
pip3 install \
    ffpyplayer \
    oscpy \
    python-osc

# Make startup script executable
chmod +x /home/pi/video_player/cluster_scripts/start_node.sh

# Create systemd service file
cat << EOF | sudo tee /etc/systemd/system/video-player.service
[Unit]
Description=Video Player Node
After=network.target

[Service]
ExecStart=/home/pi/video_player/cluster_scripts/start_node.sh \${NODE_TYPE}
WorkingDirectory=/home/pi/video_player
User=pi
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl enable video-player

# Note: NODE_TYPE should be set in /etc/environment on each machine 