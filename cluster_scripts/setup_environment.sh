#!/bin/bash

# Usage: ./setup_environment.sh [master-hor1|master-ver1|hor2|ver2]

if [ -z "$1" ]; then
    echo "Usage: $0 [master-hor1|master-ver1|hor2|ver2]"
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

echo "Environment variables set. Please reboot the system." 