import json
import os
import vlc
import time
import random
import argparse

def get_absolute_audio_path(relative_path):
    base_dir = '/home/pi/video_player'
    return os.path.join(base_dir, relative_path)

class OfflineAudioPlayer:
    def __init__(self, device_name):
        print(f"\n=== Offline Audio Player Initialization for {device_name} ===")
        
        # Hide cursor
        os.system('setterm -cursor off')
        
        self.device_name = device_name
        self.device_number = int(device_name[3])
        self.current_seed = 1
        
        # Basic VLC initialization with minimal arguments
        # Let VLC handle audio device selection through its preferences
        vlc_args = [
            '--no-video',            # Disable video output
            '--quiet'                # Minimal logging
        ]
        
        self.instance = vlc.Instance(' '.join(vlc_args))
        self.player = self.instance.media_player_new()
        
        # Set audio output to HDMI using VLC's own methods
        self.player.audio_output_device_type = "HDMI"
        self.player.audio_output_device_set("alsa", "hw:1,0")  # vc4hdmi0
        
        # Set audio volume to maximum
        self.player.audio_set_volume(100)
        
        # Define the audio files
        self.audio_files = [
            {"name": "drone_81.WAV", "duration": 437},
            {"name": "drone_82.WAV", "duration": 376},
            {"name": "drone_83.WAV", "duration": 283},
            {"name": "drone_84.WAV", "duration": 425},
        ]
        
        # Convert relative paths to absolute
        for audio in self.audio_files:
            audio['path'] = get_absolute_audio_path(f"audios/{audio['name']}")
            
        # Check if audio files exist
        for audio in self.audio_files:
            if os.path.exists(audio['path']):
                print(f"Found audio file: {audio['path']}")
            else:
                print(f"WARNING: Audio file not found: {audio['path']}")

    def _play_audio(self, audio):
        """Play a single audio file"""
        print(f"\nPlaying: {audio['name']}")
        
        try:
            # Create media with specific output settings
            media = self.instance.media_new(audio['path'])
            media.add_option(":aout=alsa")  # Force ALSA output
            media.add_option(":alsa-audio-device=hw:1,0")  # Force HDMI device
            
            self.player.set_media(media)
            self.player.play()
            
            # Set volume after loading media
            self.player.audio_set_volume(100)
            
            # Wait for audio to actually start
            while self.player.get_state() not in [vlc.State.Playing, vlc.State.Ended, vlc.State.Error]:
                time.sleep(0.1)
            
            if self.player.get_state() == vlc.State.Error:
                print("Error starting audio")
                return
            
            # Wait for exact duration
            time.sleep(audio['duration'])
            
            # Stop playback
            self.player.stop()
            
        except Exception as e:
            print(f"Error playing audio: {e}")

    def prepare_playlist(self):
        """Prepare a shuffled playlist based on device number"""
        random.seed(self.current_seed)
        
        # Create a copy of audio files and shuffle it
        playlist = self.audio_files.copy()
        random.shuffle(playlist)
        
        # Each device gets one audio file based on its number
        # hor1/ver1 get index 0 or 2, hor2/ver2 get index 1 or 3
        start_idx = (self.device_number - 1) * 2
        return [playlist[start_idx]]

    def run_player(self):
        """Main playback loop"""
        print("\n=== Starting Offline Audio Playback ===")
        
        while True:
            print(f"\n=== Starting playback with seed {self.current_seed} ===")
            
            playlist = self.prepare_playlist()
            print(f"Playing audio file in this rotation: {playlist[0]['name']}")
            
            for audio in playlist:
                self._play_audio(audio)
            
            self.current_seed += 1
            print(f"\n=== Completed seed {self.current_seed-1}, moving to seed {self.current_seed} ===")

def main():
    parser = argparse.ArgumentParser(description='Offline Audio Player')
    parser.add_argument('--device', required=True, 
                      choices=['hor1', 'hor2', 'ver1', 'ver2'],
                      help='Device name (hor1/hor2/ver1/ver2)')
    
    args = parser.parse_args()
    
    try:
        player = OfflineAudioPlayer(args.device)
        player.run_player()
    except KeyboardInterrupt:
        print("\nPlayback terminated by user")
    except Exception as e:
        print(f"\nError in playback: {e}")

if __name__ == "__main__":
    main() 