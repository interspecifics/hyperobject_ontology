# Video Player Cluster Setup Instructions

This guide explains how to set up and run the video player cluster consisting of one master node and four slave nodes (2 horizontal and 2 vertical displays).

## System Requirements

- 5 Raspberry Pi devices (one master, four slaves)
- Network switch/router
- Ethernet cables
- HDMI displays (2 horizontal, 2 vertical)
- Power supplies for all devices

## Directory Structure Setup

1. Create the required directories on each Raspberry Pi:
```bash
mkdir -p /home/pi/video_player/cluster_scripts
mkdir -p /home/pi/video_player/logs
```

2. Copy all files to the appropriate directories:
```bash
# Copy the main Python scripts
cp ho_master.py /home/pi/video_player/
cp ho_slave.py /home/pi/video_player/
cp ontology_map.json /home/pi/video_player/

# Copy the cluster scripts
cp cluster_scripts/* /home/pi/video_player/cluster_scripts/
```

## Network Configuration

The cluster uses static IP addresses:
- Master Node: 192.168.1.100
- Horizontal Display 1: 192.168.1.101
- Horizontal Display 2: 192.168.1.102
- Vertical Display 1: 192.168.1.103
- Vertical Display 2: 192.168.1.104

## Installation

1. Run the installation script on each Raspberry Pi with the appropriate IP suffix:

```bash
# On master node:
IP_SUFFIX=100 /home/pi/video_player/cluster_scripts/install_dependencies.sh

# On horizontal1:
IP_SUFFIX=101 /home/pi/video_player/cluster_scripts/install_dependencies.sh

# On horizontal2:
IP_SUFFIX=102 /home/pi/video_player/cluster_scripts/install_dependencies.sh

# On vertical1:
IP_SUFFIX=103 /home/pi/video_player/cluster_scripts/install_dependencies.sh

# On vertical2:
IP_SUFFIX=104 /home/pi/video_player/cluster_scripts/install_dependencies.sh
```

2. Make all scripts executable:
```bash
chmod +x /home/pi/video_player/cluster_scripts/*.sh
```

## Starting the Cluster

The cluster will start automatically on boot thanks to the systemd service. However, you can manually start/stop the service:

```bash
# Start the service
sudo systemctl start video-player

# Stop the service
sudo systemctl stop video-player

# Check status
sudo systemctl status video-player

# View logs
tail -f /home/pi/video_player/logs/[node_name].log
```

## Troubleshooting

1. Check node connectivity:
```bash
ping 192.168.1.100  # Master node
ping 192.168.1.101  # Horizontal 1
ping 192.168.1.102  # Horizontal 2
ping 192.168.1.103  # Vertical 1
ping 192.168.1.104  # Vertical 2
```

2. Check service status:
```bash
sudo systemctl status video-player
```

3. View logs:
```bash
# Master node logs
tail -f /home/pi/video_player/logs/master.log

# Slave nodes logs
tail -f /home/pi/video_player/logs/horizontal1.log
tail -f /home/pi/video_player/logs/horizontal2.log
tail -f /home/pi/video_player/logs/vertical1.log
tail -f /home/pi/video_player/logs/vertical2.log
```

4. Common issues:
   - If a display is not showing video, check the HDMI connection
   - If nodes aren't communicating, verify network settings
   - If videos don't play, ensure the video files exist in the correct paths

## Video Organization

Videos are organized in the `ontology_map.json` file by:
- Category
- Orientation (horizontal/vertical)
- Duration
- Resolution

The master node will automatically:
1. Distribute videos to appropriate displays based on orientation
2. Rotate through categories
3. Synchronize playback across all displays

## Maintenance

1. To update video metadata:
```bash
# Edit the ontology file
nano /home/pi/video_player/ontology_map.json

# Restart the service
sudo systemctl restart video-player
```

2. To add new videos:
   - Add video files to appropriate directories
   - Update the ontology_map.json file
   - Restart the service

3. Regular maintenance:
```bash
# Check disk space
df -h

# Check system logs
sudo journalctl -u video-player

# Update system
sudo apt update && sudo apt upgrade
```

## Safety Notes

1. Always properly shut down the Raspberry Pis:
```bash
sudo shutdown -h now
```

2. Ensure proper ventilation for all devices

3. Monitor system temperature:
```bash
vcgencmd measure_temp
```