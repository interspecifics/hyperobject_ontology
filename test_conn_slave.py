from oscpy.server import OSCThreadServer
import argparse
import time
from threading import Event

class TestSlaveNode:
    def __init__(self, orientation, node):
        print(f"\n=== OSC Slave Test Node ===")
        print(f"Initializing test slave node {node} with orientation {orientation}")
        
        self.orientation = orientation
        self.node = node
        self.stop_event = Event()
        
        # Initialize OSC server
        self.osc_server = OSCThreadServer()
        port = self._get_port(orientation, node)
        
        try:
            self.sock = self.osc_server.listen(
                address='0.0.0.0',
                port=port,
                default=True
            )
            print(f"Listening on port {port}")
        except Exception as e:
            print(f"Error binding OSC server: {e}")
            raise
        
        # Register OSC handlers
        self.osc_server.bind(b'/play', self.handle_play)
        self.osc_server.bind(b'/stop', self.handle_stop)

    def _get_port(self, orientation, node):
        """Get the correct port based on orientation and node number"""
        if orientation == "hor":
            return 8001 if node == 1 else 8002
        else:
            return 8003 if node == 1 else 8004

    def handle_play(self, video_name):
        """Handle incoming play command"""
        video_name = video_name.decode()
        print(f"\nReceived play command for: {video_name}")
        print("Would start playing video here...")

    def handle_stop(self):
        """Handle stop command"""
        print("\nReceived stop command")
        print("Would stop video here...")

    def run(self):
        """Main loop"""
        print("\nTest slave node running. Press Ctrl+C to exit...")
        try:
            while not self.stop_event.is_set():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error in main loop: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Test Slave OSC Communication')
    parser.add_argument('--orientation', required=True, choices=['hor', 'ver'],
                      help='Display orientation (hor/ver)')
    parser.add_argument('--node', required=True, type=int, choices=[1, 2],
                      help='Node number (1 or 2)')
    args = parser.parse_args()
    
    try:
        slave = TestSlaveNode(args.orientation, args.node)
        slave.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 