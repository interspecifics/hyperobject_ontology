# Video Player Cluster Setup Instructions

This guide explains how to set up and run the video player cluster using 4 Raspberry Pi devices.

## Network Configuration

The cluster uses static IP addresses in the 192.168.1.2xx range:
- Master + Display 1: 192.168.1.201 (runs both master and hor1 or ver1)
- Horizontal Display 2: 192.168.1.202
- Vertical Display 2: 192.168.1.204

## Installation

1. Copy all files to /home/pi/video_player/

2. Set up the environment:
```bash
# Make scripts executable
chmod +x /home/pi/video_player/cluster_scripts/*.sh

# Set up environment variables (choose one):
# For master + horizontal1:
sudo /home/pi/video_player/cluster_scripts/setup_environment.sh master-hor1

# OR for master + vertical1:
sudo /home/pi/video_player/cluster_scripts/setup_environment.sh master-ver1

# OR for horizontal2:
sudo /home/pi/video_player/cluster_scripts/setup_environment.sh hor2

# OR for vertical2:
sudo /home/pi/video_player/cluster_scripts/setup_environment.sh ver2
```

3. Run the installation script:
```bash
/home/pi/video_player/cluster_scripts/install_dependencies.sh
```

4. Reboot the system:
```bash
sudo reboot
```

The video player will start automatically after reboot.

## Manual Start/Stop

To stop the video player:
```bash
pkill -f "python3 ho_"
```

To start manually:
```bash
/home/pi/video_player/cluster_scripts/start_node.sh $NODE_TYPE
```

## Troubleshooting

1. Check node connectivity:
```bash
ping 192.168.1.201  # Master + Display 1
ping 192.168.1.202  # Horizontal 2
ping 192.168.1.204  # Vertical 2
```

2. View logs:
```bash
# On master+display node:
tail -f /home/pi/video_player/logs/master.log
tail -f /home/pi/video_player/logs/horizontal1.log  # or vertical1.log

# On other nodes:
tail -f /home/pi/video_player/logs/horizontal2.log
tail -f /home/pi/video_player/logs/vertical2.log
```
