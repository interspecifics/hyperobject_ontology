#!/bin/bash

# Usage: ./start_node.sh [master-hor1|master-ver1|hor2|ver2]

# Create log directory if it doesn't exist
mkdir -p /home/pi/video_player/logs

case "$1" in
    "master-hor1")
        IP="192.168.1.201"  # This node will be both master and horizontal1
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        # Start master in background
        python3 ho_master.py >> /home/pi/video_player/logs/master.log 2>&1 &
        # Start horizontal1 slave
        python3 ho_slave.py --orientation hor --node 1 >> /home/pi/video_player/logs/horizontal1.log 2>&1
        ;;
    "master-ver1")
        IP="192.168.1.203"  # This node will be both master and vertical1
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        # Start master in background
        python3 ho_master.py >> /home/pi/video_player/logs/master.log 2>&1 &
        # Start vertical1 slave
        python3 ho_slave.py --orientation ver --node 1 >> /home/pi/video_player/logs/vertical1.log 2>&1
        ;;
    "hor2")
        IP="192.168.1.202"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        python3 ho_slave.py --orientation hor --node 2 >> /home/pi/video_player/logs/horizontal2.log 2>&1
        ;;
    "ver2")
        IP="192.168.1.204"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        python3 ho_slave.py --orientation ver --node 2 >> /home/pi/video_player/logs/vertical2.log 2>&1
        ;;
    *)
        echo "Usage: $0 [master-hor1|master-ver1|hor2|ver2]"
        exit 1
        ;;
esac 