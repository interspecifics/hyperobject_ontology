# Video Player Cluster Setup Instructions

This guide explains how to set up and run the video player cluster using 4 Raspberry Pi devices.

## Network Configuration

The cluster uses static IP addresses in the 192.168.1.2xx range. There are two possible configurations:

### Configuration 1: master-ver1 (203)
- Device 1 (master-ver1): 192.168.1.203 (runs master + ver1)
- Device 2 (hor1): 192.168.1.201
- Device 3 (ver2): 192.168.1.204
- Device 4 (hor2): 192.168.1.202

### Configuration 2: master-hor1 (201)
- Device 1 (master-hor1): 192.168.1.201 (runs master + hor1)
- Device 2 (ver1): 192.168.1.203
- Device 3 (ver2): 192.168.1.204
- Device 4 (hor2): 192.168.1.202

## Installation

1. Copy all files to /home/pi/video_player/

2. Make scripts executable:
```bash
chmod +x /home/pi/video_player/cluster_scripts/*.sh
```

3. Set up environment based on device role:

For Configuration 1 (master-ver1):
```bash
# On Device 1 (master + ver1):
sudo ./cluster_scripts/setup_environment.sh master-ver1

# On Device 2 (hor1):
sudo ./cluster_scripts/setup_environment.sh hor1

# On Device 3 (ver2):
sudo ./cluster_scripts/setup_environment.sh ver2

# On Device 4 (hor2):
sudo ./cluster_scripts/setup_environment.sh hor2
```

For Configuration 2 (master-hor1):
```bash
# On Device 1 (master + hor1):
sudo ./cluster_scripts/setup_environment.sh master-hor1

# On Device 2 (ver1):
sudo ./cluster_scripts/setup_environment.sh ver1

# On Device 3 (ver2):
sudo ./cluster_scripts/setup_environment.sh ver2

# On Device 4 (hor2):
sudo ./cluster_scripts/setup_environment.sh hor2
```

4. Run the installation script on each device:
```bash
./cluster_scripts/install_dependencies.sh
```

5. Reboot all devices:
```bash
sudo reboot
```

The video player will start automatically after reboot on each device.

## Manual Control

To stop the video player:
```bash
pkill -f "python3 ho_"
```

To start manually:
```bash
/home/pi/video_player/cluster_scripts/start_node.sh $NODE_TYPE
```

## Testing

To test a single node:
```bash
# On master node
python3 /home/pi/video_player/test_master.py
```

## Troubleshooting

1. Check node connectivity:
```bash
# From any device
ping 192.168.1.201  # hor1
ping 192.168.1.202  # hor2
ping 192.168.1.203  # ver1
ping 192.168.1.204  # ver2
```

2. View logs:
```bash
# On master node:
tail -f /home/pi/video_player/logs/master.log
tail -f /home/pi/video_player/logs/horizontal1.log  # or vertical1.log

# On other nodes:
tail -f /home/pi/video_player/logs/horizontal1.log
tail -f /home/pi/video_player/logs/vertical1.log
tail -f /home/pi/video_player/logs/horizontal2.log
tail -f /home/pi/video_player/logs/vertical2.log
```

3. Check virtual environment:
```bash
source /home/pi/video_player/venv/bin/activate
python3 -c "import pygame; import ffpyplayer; import oscpy"
```
