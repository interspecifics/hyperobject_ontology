#!/bin/bash

# Usage: ./start_node.sh [master-hor1|master-ver1|hor1|hor2|ver1|ver2]

# Create log directory if it doesn't exist
mkdir -p /home/pi/video_player/logs

# Activate virtual environment
source /home/pi/video_player/venv/bin/activate

# Function to log messages with timestamps
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /home/pi/video_player/logs/start_node.log
}

log_message "Starting node with type: $1"

case "$1" in
    "master-hor1")
        IP="192.168.1.201"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting master node on $IP"
        python3 ho_master.py >> /home/pi/video_player/logs/master.log 2>&1 &
        MASTER_PID=$!
        log_message "Master started with PID: $MASTER_PID"
        log_message "Starting horizontal1 slave"
        python3 ho_slave.py --orientation hor --node 1 >> /home/pi/video_player/logs/horizontal1.log 2>&1
        ;;
    "master-ver1")
        IP="192.168.1.203"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting master node on $IP"
        python3 ho_master.py >> /home/pi/video_player/logs/master.log 2>&1 &
        MASTER_PID=$!
        log_message "Master started with PID: $MASTER_PID"
        log_message "Starting vertical1 slave"
        python3 ho_slave.py --orientation ver --node 1 >> /home/pi/video_player/logs/vertical1.log 2>&1
        ;;
    "hor1")
        IP="192.168.1.201"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting horizontal1 slave on $IP"
        python3 ho_slave.py --orientation hor --node 1 >> /home/pi/video_player/logs/horizontal1.log 2>&1
        ;;
    "hor2")
        IP="192.168.1.202"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting horizontal2 slave on $IP"
        python3 ho_slave.py --orientation hor --node 2 >> /home/pi/video_player/logs/horizontal2.log 2>&1
        ;;
    "ver1")
        IP="192.168.1.203"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting vertical1 slave on $IP"
        python3 ho_slave.py --orientation ver --node 1 >> /home/pi/video_player/logs/vertical1.log 2>&1
        ;;
    "ver2")
        IP="192.168.1.204"
        sudo ip addr add $IP/24 dev eth0
        cd /home/pi/video_player
        log_message "Starting vertical2 slave on $IP"
        python3 ho_slave.py --orientation ver --node 2 >> /home/pi/video_player/logs/vertical2.log 2>&1
        ;;
    *)
        echo "Usage: $0 [master-hor1|master-ver1|hor1|hor2|ver1|ver2]"
        exit 1
        ;;
esac

# Cleanup function
cleanup() {
    log_message "Shutting down node..."
    if [ ! -z "$MASTER_PID" ]; then
        kill $MASTER_PID
    fi
    deactivate
    log_message "Shutdown complete"
}

# Set up trap for cleanup
trap cleanup EXIT

# Keep the script running
wait 