# Video Player Cluster Setup Instructions

This guide explains how to set up and run the synchronized video player cluster using 4 Raspberry Pi devices.

## System Architecture

The system consists of:
- 1 master node (which also runs a slave)
- 3 additional slave nodes
- 2 horizontal displays (1920x1080)
- 2 vertical displays (768x1280 or 1080x1920)

### Network Configuration

The cluster uses fixed IP addresses and ports:

| Node    | IP Address      | Port | Description                    |
|---------|----------------|------|--------------------------------|
| hor1    | 192.168.1.201  | 8001 | Horizontal display 1          |
| hor2    | 192.168.1.202  | 8002 | Horizontal display 2          |
| ver1    | 192.168.1.203  | 8003 | Vertical display 1           |
| ver2    | 192.168.1.204  | 8004 | Vertical display 2           |

The master node typically runs on the same device as either hor1 or ver1.

## Installation

1. Copy all files to /home/pi/video_player/ on each device:
```bash
scp -r * pi@192.168.1.xxx:/home/pi/video_player/
```

2. Make scripts executable:
```bash
chmod +x /home/pi/video_player/cluster_scripts/*.sh
```

3. Install dependencies on each device:
```bash
./cluster_scripts/install_dependencies.sh
```

## Configuration

Each device needs to be configured based on its role:

### Master + Slave Node (hor1)
```bash
# On 192.168.1.201
python3 ho_master.py --local-slave hor1
python3 ho_slave.py --orientation hor --node 1
```

### Slave Nodes
```bash
# On 192.168.1.202 (hor2)
python3 ho_slave.py --orientation hor --node 2

# On 192.168.1.203 (ver1)
python3 ho_slave.py --orientation ver --node 1

# On 192.168.1.204 (ver2)
python3 ho_slave.py --orientation ver --node 2
```

## Operation

The system will:
1. Process categories in alphabetical order
2. Play animated videos distributed across node pairs
3. Insert text videos at intervals (never simultaneously)
4. Maintain synchronization across all displays

### Video Types
- Animated videos are distributed between node pairs
- Text videos are shown on one node while its pair waits
- No two text videos play simultaneously across the system

## Testing

To test a single node:
```bash
python3 test_slave.py --orientation [hor|ver]
```

This will play through all categories with proper video type alternation.

## Troubleshooting

1. Check network connectivity:
```bash
ping 192.168.1.201  # hor1
ping 192.168.1.202  # hor2
ping 192.168.1.203  # ver1
ping 192.168.1.204  # ver2
```

2. Verify OSC communication:
```bash
# On slave nodes
netstat -an | grep 800[1-4]
```

3. Common issues:
- Black screen: Check if pygame is in fullscreen mode
- No video: Verify video paths in ontology_map.json
- Desynchronization: Check network latency between nodes

4. Restart a node:
```bash
# Stop all python processes
pkill -f "python3 ho_"

# Restart slave
python3 ho_slave.py --orientation [hor|ver] --node [1|2]

# Restart master (if applicable)
python3 ho_master.py --local-slave [hor1|ver1]
```

## File Structure
```
/home/pi/video_player/
├── ho_master.py      # Master node controller
├── ho_slave.py       # Slave node video player
├── test_slave.py     # Single node test script
├── ontology_map.json # Video metadata
└── cluster_scripts/  # Setup and management scripts
```

## Logs

Logs are written to:
```
/home/pi/video_player/logs/
├── master.log
├── horizontal1.log
├── horizontal2.log
├── vertical1.log
└── vertical2.log
```

Monitor logs in real-time:
```bash
tail -f /home/pi/video_player/logs/*.log
```
