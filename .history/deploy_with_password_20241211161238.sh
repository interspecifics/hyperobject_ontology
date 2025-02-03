#!/bin/bash

# Configuration
VIDEO_PLAYER_DIR="/home/pi/video_player"
SOURCE_DIR="."
PASSWORD="1234"  # Replace with actual password

# Add package directory
PACKAGES_DIR="./packages"

# Define host-to-type mappings as separate arrays
HOSTS=(
    "master001.local"
    "slave002.local"
    "slave003.local"
    "slave004.local"
)

NODE_TYPES=(
    "hor1"
    "hor2"
    "ver1"
    "ver2"
)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Download packages if they don't exist
download_packages() {
    echo "Checking and downloading required packages..."
    mkdir -p "${PACKAGES_DIR}"
    
    if [ ! -f "${PACKAGES_DIR}/unclutter.deb" ]; then
        echo "Downloading unclutter package..."
        # Using the Debian Bullseye repository for armhf architecture
        wget -O "${PACKAGES_DIR}/unclutter.deb" \
            "http://archive.raspberrypi.org/debian/pool/main/u/unclutter/unclutter_8-2+rpt1_armhf.deb"
    fi
}

# Function to deploy to a single host
deploy_to_host() {
    local host=$1
    local node_type=$2
    echo -e "${GREEN}Deploying to ${host} as ${node_type}...${NC}"
    
    # Create packages directory on remote
    sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" "mkdir -p ${VIDEO_PLAYER_DIR}/packages"
    
    # Copy package files
    echo "Copying package files..."
    sshpass -p "${PASSWORD}" scp -r -o StrictHostKeyChecking=no \
        "${PACKAGES_DIR}/unclutter.deb" \
        "pi@${host}:${VIDEO_PLAYER_DIR}/packages/"
    
    # Install packages
    echo "Installing packages..."
    sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" "
        cd ${VIDEO_PLAYER_DIR}/packages && \
        sudo dpkg -i unclutter.deb
    "
    
    # Add to known_hosts if not already present (suppressing warnings)
    ssh-keygen -R "${host}" 2>/dev/null
    ssh-keyscan -H "${host}" >> ~/.ssh/known_hosts 2>/dev/null
    
    # Create directory if it doesn't exist
    sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" "mkdir -p ${VIDEO_PLAYER_DIR}"
    
    # Copy the Python files
    echo "Copying Python files..."
    sshpass -p "${PASSWORD}" scp -r -o StrictHostKeyChecking=no \
        "${SOURCE_DIR}/offline_slave.py" \
        "${SOURCE_DIR}/ontology_map.json" \
        "pi@${host}:${VIDEO_PLAYER_DIR}/"
    
    # Clear and recreate logs directory
    echo "Clearing and recreating logs directory..."
    sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" \
        "rm -rf ${VIDEO_PLAYER_DIR}/logs && mkdir -p ${VIDEO_PLAYER_DIR}/logs"
    
    # Determine which script to run based on node type (currently overrriding)
    if [[ $node_type == hor* ]]; then
        STARTUP_CMD="python3 ${VIDEO_PLAYER_DIR}/offline_slave.py --device ${node_type}"
    else
        STARTUP_CMD="python3 ${VIDEO_PLAYER_DIR}/offline_slave.py --device ${node_type}"
    
    # Update autostart to include unclutter and video player
    sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" "
        # Remove any existing autostart entries
        rm -f ~/.config/autostart/videoplayer.desktop
        rm -f ~/.config/autostart/unclutter.desktop
        
        # Create fresh autostart directory
        mkdir -p ~/.config/autostart
        
        # Create unclutter autostart entry
        cat > ~/.config/autostart/unclutter.desktop << EOF
[Desktop Entry]
Type=Application
Name=Unclutter
Exec=unclutter -idle 0
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOF
        
        # Create video player autostart entry
        cat > ~/.config/autostart/videoplayer.desktop << EOF
[Desktop Entry]
Type=Application
Name=Video Player
Exec=lxterminal -e 'export DISPLAY=:0; cd ${VIDEO_PLAYER_DIR}; ${STARTUP_CMD}'
Terminal=true
Hidden=false
X-GNOME-Autostart-enabled=true
EOF
        
        chmod +x ~/.config/autostart/unclutter.desktop
        chmod +x ~/.config/autostart/videoplayer.desktop
    "
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully deployed to ${host}${NC}"
    else
        echo -e "${RED}Failed to deploy to ${host}${NC}"
    fi
}

# Main script execution
download_packages

# Main deployment loop
for i in "${!HOSTS[@]}"; do
    deploy_to_host "${HOSTS[$i]}" "${NODE_TYPES[$i]}"
    echo "-----------------------------------"
done

echo -e "${GREEN}Deployment complete!${NC}"

# Optional: Reboot all devices
echo "Would you like to reboot all devices? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
    for host in "${HOSTS[@]}"; do
        echo "Rebooting ${host}..."
        sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" "sudo reboot"
    done
fi 