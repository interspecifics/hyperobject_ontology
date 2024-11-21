import json
import time
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

class TestMaster:
    def __init__(self):
        # Load video metadata
        with open('ontology_map.json', 'r') as f:
            self.videos = json.load(f)
            
        # Initialize OSC server
        self.osc_server = OSCThreadServer()
        self.sock = self.osc_server.listen(address='0.0.0.0', port=7000, default=True)
        
        # Track connected slave
        self.slave_id = None
        self.slave_orientation = None
        self.slave_client = None
        
        # Register handler
        self.osc_server.bind(b'/slave/announce', self.handle_slave_announce)
        
    def handle_slave_announce(self, slave_id, orientation):
        slave_id = slave_id.decode()
        orientation = orientation.decode()
        print(f"Slave connected: {slave_id} ({orientation})")
        
        self.slave_id = slave_id
        self.slave_orientation = orientation
        
        # Create client for the slave
        port = 8001 if orientation == "hor" else 8002
        self.slave_client = OSCClient('192.168.1.201', port)  # Assuming first node IP
        
    def run_test_sequence(self):
        # Wait for slave to connect
        while not self.slave_client:
            print("Waiting for slave to connect...")
            time.sleep(2)
        
        print("Starting test sequence...")
        
        # Get three videos of the right orientation
        test_videos = [v for v in self.videos 
                      if v['orientation'] == self.slave_orientation][:3]
        
        # Play test sequence
        for video in test_videos:
            print(f"Playing: {video['name']}")
            self.slave_client.send_message(b'/play', [video['name'].encode()])
            
            # Wait for video duration plus a small buffer
            duration = video['duration'] + 0.5
            print(f"Waiting for {duration} seconds...")
            time.sleep(duration)

def main():
    test_master = TestMaster()
    
    try:
        test_master.run_test_sequence()
    except KeyboardInterrupt:
        print("Test terminated by user")

if __name__ == "__main__":
    main() 