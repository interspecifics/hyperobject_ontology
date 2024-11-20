#!/bin/bash

# Set static IP for second horizontal display
sudo ip addr add 192.168.1.102/24 dev eth0

# Set hostname
sudo hostnamectl set-hostname horizontal2

# Create log directory if it doesn't exist
mkdir -p /home/pi/video_player/logs

# Start the slave program with logging
cd /home/pi/video_player
python3 ho_slave.py >> /home/pi/video_player/logs/horizontal2.log 2>&1 