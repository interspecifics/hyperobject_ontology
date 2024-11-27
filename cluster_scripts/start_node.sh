#!/bin/bash

# Usage: ./start_node.sh [hor1|hor2|ver1|ver2]

# Create log directory if it doesn't exist
mkdir -p /home/pi/video_player/logs

# Set up display environment
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority

# Activate virtual environment
source /home/pi/video_player/venv/bin/activate

# Function to log messages with timestamps
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /home/pi/video_player/logs/start_node.log
}

log_message "Starting node with type: $1"

case "$1" in
    "hor1")
        IP="192.168.1.201"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting horizontal1 node with VLC player"
        python3 offline_slave.py --device hor1 >> /home/pi/video_player/logs/horizontal1.log 2>&1
        ;;
    "hor2")
        IP="192.168.1.202"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting horizontal2 node with VLC player"
        python3 offline_slave.py --device hor2 >> /home/pi/video_player/logs/horizontal2.log 2>&1
        ;;
    "ver1")
        IP="192.168.1.203"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting vertical1 node with FFPyPlayer"
        python3 offline_ffpy_slave.py --device ver1 >> /home/pi/video_player/logs/vertical1.log 2>&1
        ;;
    "ver2")
        IP="192.168.1.204"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting vertical2 node with FFPyPlayer"
        python3 offline_ffpy_slave.py --device ver2 >> /home/pi/video_player/logs/vertical2.log 2>&1
        ;;
    *)
        echo "Usage: $0 [hor1|hor2|ver1|ver2]"
        exit 1
        ;;
esac

# Cleanup function
cleanup() {
    log_message "Shutting down node..."
    pkill -f "python3 offline"
    deactivate
    log_message "Shutdown complete"
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Keep the script running
wait 