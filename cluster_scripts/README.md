# Video Player Cluster Setup Instructions

This guide explains how to set up and run the offline video player cluster using 4 Raspberry Pi devices.

## System Architecture

The system consists of:
- 2 horizontal displays (1920x1080) running offline_slave.py with VLC
- 2 vertical displays (768x1280 or 1080x1920) running offline_ffpy_slave.py with FFPyPlayer

### Network Configuration

The cluster uses fixed IP addresses:

| Node    | IP Address      | Description                    |
|---------|----------------|--------------------------------|
| hor1    | 192.168.1.201  | Horizontal display 1 (VLC)    |
| hor2    | 192.168.1.202  | Horizontal display 2 (VLC)    |
| ver1    | 192.168.1.203  | Vertical display 1 (FFPyPlayer)|
| ver2    | 192.168.1.204  | Vertical display 2 (FFPyPlayer)|

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

Each device runs independently in offline mode:

### Horizontal Nodes (VLC-based)
```bash
# On 192.168.1.201 (hor1)
python3 offline_slave.py --device hor1

# On 192.168.1.202 (hor2)
python3 offline_slave.py --device hor2
```

### Vertical Nodes (FFPyPlayer-based)
```bash
# On 192.168.1.203 (ver1)
python3 offline_ffpy_slave.py --device ver1

# On 192.168.1.204 (ver2)
python3 offline_ffpy_slave.py --device ver2
```

## Operation

Each node will:
1. Process categories in alphabetical order
2. Play animated videos based on its node number (1 or 2)
3. Insert text videos at intervals
4. Maintain loose synchronization through deterministic shuffling

### Video Types
- Animated videos are distributed between node pairs
- Text videos are shown on one node while its pair shows animated content
- Synchronization is maintained through consistent random seeds

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
