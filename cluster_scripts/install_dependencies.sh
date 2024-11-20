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

# Make all startup scripts executable
chmod +x /home/pi/video_player/cluster_scripts/start_*.sh

# Create systemd service files for auto-start
cat << EOF | sudo tee /etc/systemd/system/video-player.service
[Unit]
Description=Video Player Node
After=network.target

[Service]
ExecStart=/home/pi/video_player/cluster_scripts/start_\${HOSTNAME}.sh
WorkingDirectory=/home/pi/video_player
User=pi
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable video-player
sudo systemctl start video-player

# Add network configuration
cat << EOF | sudo tee -a /etc/dhcpcd.conf
interface eth0
static ip_address=192.168.1.\${IP_SUFFIX}/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
EOF 