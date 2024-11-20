#!/bin/bash

# Set static IP for first vertical display
sudo ip addr add 192.168.1.103/24 dev eth0

# Set hostname
sudo hostnamectl set-hostname vertical1

# Create log directory if it doesn't exist
mkdir -p /home/pi/video_player/logs

# Start the slave program with logging
cd /home/pi/video_player
python3 ho_slave.py >> /home/pi/video_player/logs/vertical1.log 2>&1 