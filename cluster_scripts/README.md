# Video Player Cluster Setup Instructions

This guide explains how to set up and run the video player cluster using 4 Raspberry Pi devices.

## Network Configuration

The cluster uses static IP addresses in the 192.168.1.2xx range:
- Master + Display 1: 192.168.1.201 (runs both master and hor1 or ver1)
- Horizontal Display 2: 192.168.1.202
- Vertical Display 2: 192.168.1.204

## Installation

1. Copy all files to /home/pi/video_player/

2. Set the node type in /etc/environment before installation:

For the master+display node (choose one):
```bash
# If this node will be master + horizontal1:
echo 'NODE_TYPE=master-hor1' | sudo tee -a /etc/environment

# OR if this node will be master + vertical1:
echo 'NODE_TYPE=master-ver1' | sudo tee -a /etc/environment
```

For other nodes:
```bash
# On horizontal2:
echo 'NODE_TYPE=hor2' | sudo tee -a /etc/environment

# On vertical2:
echo 'NODE_TYPE=ver2' | sudo tee -a /etc/environment
```

3. Run the installation script:
```bash
/home/pi/video_player/cluster_scripts/install_dependencies.sh
```

## Service Management

```bash
# Start service
sudo systemctl start video-player

# Check status
sudo systemctl status video-player

# View logs
tail -f /home/pi/video_player/logs/*.log
```

## Manual Start

You can also start nodes manually:

```bash
# On master+display node:
/home/pi/video_player/cluster_scripts/start_node.sh master-hor1  # For master + horizontal1
# OR
/home/pi/video_player/cluster_scripts/start_node.sh master-ver1  # For master + vertical1

# On other nodes:
/home/pi/video_player/cluster_scripts/start_node.sh hor2    # For horizontal 2
/home/pi/video_player/cluster_scripts/start_node.sh ver2    # For vertical 2
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
