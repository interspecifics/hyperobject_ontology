import os
import json
import subprocess
from pathlib import Path

def get_audio_duration(file_path):
    """Get audio duration using ffprobe"""
    try:
        result = subprocess.run([
            'ffprobe', 
            '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ], capture_output=True, text=True)
        
        duration = float(result.stdout.strip())
        return int(duration)  # Round down to nearest second
    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
        return None

def main():
    # Get the directory where this script is located
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    audio_dir = script_dir / 'audios'
    
    # Check if ffprobe is installed
    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True)
    except FileNotFoundError:
        print("ffprobe not found. Please install ffmpeg:")
        print("brew install ffmpeg")
        return
    
    # Check if audios directory exists
    if not audio_dir.exists():
        print(f"Audio directory not found at: {audio_dir}")
        return
    
    # Get all audio files
    audio_files = []
    supported_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg'}
    
    for file in audio_dir.iterdir():
        if file.suffix.lower() in supported_extensions:
            duration = get_audio_duration(str(file))
            if duration is not None:
                audio_files.append({
                    "name": file.name,
                    "duration": duration
                })
    
    # Sort by name
    audio_files.sort(key=lambda x: x['name'])
    
    # Print formatted Python code
    print("\nCopy this into offline_audio_slave.py:")
    print("\nself.audio_files = [")
    for audio in audio_files:
        print(f"    {{\"name\": \"{audio['name']}\", \"duration\": {audio['duration']}}},  # {audio['duration']} seconds")
    print("]")
    
    # Also save as JSON
    with open(audio_dir / 'audio_info.json', 'w') as f:
        json.dump(audio_files, f, indent=4)
    print(f"\nAudio information also saved to: {audio_dir}/audio_info.json")

if __name__ == "__main__":
    main() 