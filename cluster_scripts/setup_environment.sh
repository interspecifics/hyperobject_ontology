#!/bin/bash

# Usage: ./setup_environment.sh [master-hor1|master-ver1|hor1|hor2|ver1|ver2]

if [ -z "$1" ]; then
    echo "Usage: $0 [master-hor1|master-ver1|hor1|hor2|ver1|ver2]"
    exit 1
fi

# Add NODE_TYPE to /etc/environment if not already present
if ! grep -q "NODE_TYPE" /etc/environment; then
    echo "NODE_TYPE=$1" | sudo tee -a /etc/environment
fi

# Add DISPLAY variable if not present
if ! grep -q "DISPLAY" /etc/environment; then
    echo "DISPLAY=:0" | sudo tee -a /etc/environment
fi

# Add XAUTHORITY if not present
if ! grep -q "XAUTHORITY" /etc/environment; then
    echo "XAUTHORITY=/home/pi/.Xauthority" | sudo tee -a /etc/environment
fi

# Configure network interfaces based on node type
case "$1" in
    "master-hor1")
        echo "Configuring for master + hor1..."
        echo "NODE_IP=192.168.1.201" | sudo tee -a /etc/environment
        ;;
    "master-ver1")
        echo "Configuring for master + ver1..."
        echo "NODE_IP=192.168.1.203" | sudo tee -a /etc/environment
        ;;
    "hor1")
        echo "Configuring for hor1..."
        echo "NODE_IP=192.168.1.201" | sudo tee -a /etc/environment
        ;;
    "hor2")
        echo "Configuring for hor2..."
        echo "NODE_IP=192.168.1.202" | sudo tee -a /etc/environment
        ;;
    "ver1")
        echo "Configuring for ver1..."
        echo "NODE_IP=192.168.1.203" | sudo tee -a /etc/environment
        ;;
    "ver2")
        echo "Configuring for ver2..."
        echo "NODE_IP=192.168.1.204" | sudo tee -a /etc/environment
        ;;
    *)
        echo "Invalid node type. Use: master-hor1|master-ver1|hor1|hor2|ver1|ver2"
        exit 1
        ;;
esac

echo "Environment variables set. Please reboot the system." 