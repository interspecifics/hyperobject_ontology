#!/bin/bash

# Configuration
VIDEO_PLAYER_DIR="/home/pi/video_player"
SOURCE_DIR="."
PASSWORD="1234"  # Replace with actual password

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

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "sshpass is not installed. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Homebrew is not installed. Please install it first:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    brew install hudochenkov/sshpass/sshpass
fi

# Function to deploy to a single host
deploy_to_host() {
    local host=$1
    local node_type=$2
    echo -e "${GREEN}Deploying to ${host} as ${node_type}...${NC}"
    
    # Add to known_hosts if not already present (suppressing warnings)
    ssh-keygen -R "${host}" 2>/dev/null
    ssh-keyscan -H "${host}" >> ~/.ssh/known_hosts 2>/dev/null
    
    # Create directory if it doesn't exist
    sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" "mkdir -p ${VIDEO_PLAYER_DIR}"
    
    # Copy the Python files
    echo "Copying Python files..."
    sshpass -p "${PASSWORD}" scp -r -o StrictHostKeyChecking=no \
        "${SOURCE_DIR}/offline_slave.py" \
        "${SOURCE_DIR}/offline_ffpy_slave.py" \
        "${SOURCE_DIR}/ontology_map.json" \
        "pi@${host}:${VIDEO_PLAYER_DIR}/"
    
    # Create logs directory
    echo "Creating logs directory..."
    sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" \
        "mkdir -p ${VIDEO_PLAYER_DIR}/logs"
    
    # Determine which script to run based on node type
    if [[ $node_type == hor* ]]; then
        STARTUP_CMD="python3 ${VIDEO_PLAYER_DIR}/offline_slave.py --device ${node_type}"
    else
        STARTUP_CMD="python3 ${VIDEO_PLAYER_DIR}/offline_ffpy_slave.py --device ${node_type}"
    fi
    
    # Create autostart entry
    sshpass -p "${PASSWORD}" ssh -o StrictHostKeyChecking=no "pi@${host}" "
        # Remove any existing autostart entries
        rm -f ~/.config/autostart/videoplayer.desktop
        
        # Create fresh autostart directory
        mkdir -p ~/.config/autostart
        
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
        chmod +x ~/.config/autostart/videoplayer.desktop
    "
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully deployed to ${host}${NC}"
    else
        echo -e "${RED}Failed to deploy to ${host}${NC}"
    fi
}

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