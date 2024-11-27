#!/bin/bash

# Configuration
VIDEO_PLAYER_DIR="/home/pi/video_player"
SOURCE_DIR="."  # Current directory where your files are
HOSTS=(
    "pi@192.168.1.201"  # hor1
    "pi@192.168.1.202"  # hor2
    "pi@192.168.1.203"  # ver1
    "pi@192.168.1.204"  # ver2
)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to deploy to a single host
deploy_to_host() {
    local host=$1
    echo -e "${GREEN}Deploying to ${host}...${NC}"
    
    # Create directory if it doesn't exist
    ssh ${host} "mkdir -p ${VIDEO_PLAYER_DIR}"
    
    # Copy the Python files
    echo "Copying Python files..."
    scp "${SOURCE_DIR}/ho_master.py" \
        "${SOURCE_DIR}/ho_slave.py" \
        "${SOURCE_DIR}/offline_slave.py" \
        "${host}:${VIDEO_PLAYER_DIR}/"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully deployed to ${host}${NC}"
    else
        echo -e "${RED}Failed to deploy to ${host}${NC}"
    fi
}

# Main deployment loop
for host in "${HOSTS[@]}"; do
    deploy_to_host "$host"
    echo "-----------------------------------"
done

echo -e "${GREEN}Deployment complete!${NC}" 