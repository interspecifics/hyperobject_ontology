#!/bin/bash

# Update package list
sudo apt-get update

# Install required system packages
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-pygame \
    ffmpeg \
    python3-full

# Create project directories
mkdir -p /home/pi/video_player/logs

# Create a virtual environment
python3 -m venv /home/pi/video_player/venv

# Create activation script that can be sourced by other scripts
cat << 'EOF' > /home/pi/video_player/venv/activate_venv.sh
#!/bin/bash
source /home/pi/video_player/venv/bin/activate
EOF

chmod +x /home/pi/video_player/venv/activate_venv.sh

# Activate the virtual environment and install packages
source /home/pi/video_player/venv/bin/activate

# Install required Python packages in the virtual environment
pip install --upgrade pip
pip install \
    ffpyplayer \
    oscpy

# Deactivate the virtual environment
deactivate

# Make startup script executable
chmod +x /home/pi/video_player/cluster_scripts/start_node.sh

# Create log directory with proper permissions
sudo mkdir -p /home/pi/video_player/logs
sudo chown -R pi:pi /home/pi/video_player/logs

# Add startup command to .bashrc if not already present
STARTUP_CMD="# Start Video Player\nif [ -z \"\$SSH_CLIENT\" ] && [ -z \"\$SSH_TTY\" ]; then\n    /home/pi/video_player/cluster_scripts/start_node.sh \$NODE_TYPE\nfi"
if ! grep -q "Start Video Player" /home/pi/.bashrc; then
    echo -e "\n${STARTUP_CMD}" >> /home/pi/.bashrc
fi

echo "Installation complete. Please set NODE_TYPE in /etc/environment"