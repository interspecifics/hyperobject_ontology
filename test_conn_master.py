from oscpy.client import OSCClient
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description='Test Master OSC Communication')
    parser.add_argument('--target', required=True, choices=['hor1', 'hor2', 'ver1', 'ver2'],
                      help='Target slave to test (hor1/hor2/ver1/ver2)')
    args = parser.parse_args()

    # Map target to port and hostname
    target_map = {
        'hor1': {'port': 8001, 'host': 'master001.local'},
        'hor2': {'port': 8002, 'host': 'slave002.local'},
        'ver1': {'port': 8003, 'host': 'slave003.local'},
        'ver2': {'port': 8004, 'host': 'slave004.local'}
    }

    target_info = target_map[args.target]
    hostname = target_info['host']
    port = target_info['port']
    
    print(f"\n=== OSC Master Test Node ===")
    print(f"Target: {args.target} on {hostname}:{port}")

    try:
        # Create OSC client with the hostname
        osc = OSCClient(hostname, port)
        print(f"OSC client initialized")

        # Test sequence
        print("\nStarting test sequence...")
        
        # Test play command
        test_video = "test_video"
        print(f"\nSending play command for: {test_video}")
        osc.send_message(b'/play', [test_video.encode()])
        time.sleep(2)

        # Test stop command
        print("\nSending stop command")
        osc.send_message(b'/stop', [])
        time.sleep(1)

        print("\nTest sequence completed")

    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    main() 