import json
import time
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/video_player/logs/test_master.log'),
        logging.StreamHandler()
    ]
)

class TestMaster:
    def __init__(self):
        logging.info("Initializing Test Master...")
        
        # Load video metadata
        try:
            with open('/home/pi/video_player/ontology_map.json', 'r') as f:
                self.videos = json.load(f)
            logging.info("Loaded video metadata successfully")
        except Exception as e:
            logging.error(f"Error loading video metadata: {e}")
            raise
            
        # Initialize OSC server
        try:
            self.osc_server = OSCThreadServer()
            self.sock = self.osc_server.listen(address='192.168.1.200', port=7000, default=True)
            logging.info("OSC server listening on port 7000")
        except Exception as e:
            logging.error(f"Error initializing OSC server: {e}")
            raise
        
        # Track connected slave
        self.slave_id = None
        self.slave_orientation = None
        self.slave_client = None
        
        # Register handler
        self.osc_server.bind(b'/slave/announce', self.handle_slave_announce)
        logging.info("Registered slave announcement handler")
        
    def handle_slave_announce(self, slave_id, orientation):
        try:
            slave_id = slave_id.decode()
            orientation = orientation.decode()
            logging.info(f"Received slave announcement - ID: {slave_id}, Orientation: {orientation}")
            
            self.slave_id = slave_id
            self.slave_orientation = orientation
            
            # Create client for the slave
            ip = f"192.168.1.{slave_id}"
            port = 8001 if orientation == "hor" else 8002
            self.slave_client = OSCClient(ip, port)
            logging.info(f"Created client connection to slave at {ip}:{port}")
        except Exception as e:
            logging.error(f"Error in handle_slave_announce: {e}")
            raise

    def run_test_sequence(self):
        """Run a test sequence of videos"""
        # Wait for slave to connect
        while not self.slave_client:
            logging.info("Waiting for slave to connect...")
            time.sleep(2)
        
        logging.info("Starting test sequence...")
        
        # Get three videos of the right orientation
        test_videos = [v for v in self.videos 
                      if v['orientation'] == self.slave_orientation][:5]
        
        if not test_videos:
            logging.info(f"No videos found for orientation: {self.slave_orientation}")
            return
            
        # Send all videos to queue immediately
        for video in test_videos:
            logging.info(f"Queueing: {video['name']}")
            self.slave_client.send_message(b'/play', [video['name'].encode()])
            time.sleep(0.1)  # Small delay to prevent message congestion
        
        # Wait for the total duration of all videos plus some buffer
        total_duration = sum(v['duration'] for v in test_videos) + 2
        logging.info(f"Waiting for sequence to complete (approx {total_duration} seconds)...")
        time.sleep(total_duration)
        logging.info("Test sequence completed")

def main():
    try:
        test_master = TestMaster()
        logging.info("Test master created, entering main loop...")
        test_master.run_test_sequence()
    except KeyboardInterrupt:
        logging.info("Test terminated by user")
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    # Ensure log directory exists
    os.makedirs('/home/pi/video_player/logs', exist_ok=True)
    main() 