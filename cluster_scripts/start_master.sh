#!/bin/bash

# Set static IP for master node
sudo ip addr add 192.168.1.100/24 dev eth0

# Set hostname
sudo hostnamectl set-hostname master-node

# Create log directory if it doesn't exist
mkdir -p /home/pi/video_player/logs

# Start the master program with logging
cd /home/pi/video_player
python3 ho_master.py >> /home/pi/video_player/logs/master.log 2>&1 