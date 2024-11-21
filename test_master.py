import json
import time
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

class TestMaster:
    def __init__(self):
        print("Initializing Test Master...")
        
        # Load video metadata
        try:
            with open('ontology_map.json', 'r') as f:
                self.videos = json.load(f)
            print("Loaded video metadata successfully")
        except Exception as e:
            print(f"Error loading video metadata: {e}")
            raise
            
        # Initialize OSC server
        try:
            self.osc_server = OSCThreadServer()
            self.sock = self.osc_server.listen(address='0.0.0.0', port=7000, default=True)
            print("OSC server listening on port 7000")
        except Exception as e:
            print(f"Error initializing OSC server: {e}")
            raise
        
        # Track connected slave
        self.slave_id = None
        self.slave_orientation = None
        self.slave_client = None
        
        # Register handler
        self.osc_server.bind(b'/slave/announce', self.handle_slave_announce)
        print("Registered slave announcement handler")
        print("Master initialized and waiting for slaves...")
        
    def handle_slave_announce(self, slave_id, orientation):
        try:
            slave_id = slave_id.decode()
            orientation = orientation.decode()
            print(f"Received slave announcement - ID: {slave_id}, Orientation: {orientation}")
            
            self.slave_id = slave_id
            self.slave_orientation = orientation
            
            # Create client for the slave
            port = 8001 if orientation == "hor" else 8002
            self.slave_client = OSCClient('127.0.0.1', port)
            print(f"Created client connection to slave on port {port}")
        except Exception as e:
            print(f"Error in handle_slave_announce: {e}")
            raise

    def run_test_sequence(self):
        """Run a test sequence of videos"""
        # Wait for slave to connect
        while not self.slave_client:
            print("Waiting for slave to connect...")
            time.sleep(2)
        
        print("Starting test sequence...")
        
        # Get three videos of the right orientation
        test_videos = [v for v in self.videos 
                      if v['orientation'] == self.slave_orientation][:5]
        
        if not test_videos:
            print(f"No videos found for orientation: {self.slave_orientation}")
            return
            
        # Send all videos to queue immediately
        for video in test_videos:
            print(f"Queueing: {video['name']}")
            self.slave_client.send_message(b'/play', [video['name'].encode()])
            time.sleep(0.1)  # Small delay to prevent message congestion
        
        # Wait for the total duration of all videos plus some buffer
        total_duration = sum(v['duration'] for v in test_videos) + 2
        print(f"Waiting for sequence to complete (approx {total_duration} seconds)...")
        time.sleep(total_duration)
        print("Test sequence completed")

def main():
    try:
        test_master = TestMaster()
        print("Test master created, entering main loop...")
        test_master.run_test_sequence()
    except KeyboardInterrupt:
        print("Test terminated by user")
    except Exception as e:
        print(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 