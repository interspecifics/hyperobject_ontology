import os
import json
import cv2
from pathlib import Path
import re

class VideoOntologyMapper:
    """
    A class that maps the video archive of a hyperobject ontology.
    It analyzes video files to create a structured database that captures their:
    - Hierarchical categorization (hyperobject categories, spatial orientations)
    - Technical metadata (dimensions, duration)
    - File relationships and archival properties
    
    This creates a semantic index of how videos document and represent hyperobjects
    through their organization, metadata, and relationships.
    """

    def __init__(self, root_dir="Videos_hd_final"):
        """
        Initialize the hyperobject video mapper with a root archive directory.

        Args:
            root_dir (str): Root directory containing the hyperobject video collection. Defaults to "Generados".
        """
        self.root_dir = Path(root_dir)
        self.database = []
        self.orientation_patterns = re.compile(r'^(hor|ver)', re.IGNORECASE)

    def get_video_metadata(self, video_path):
        """
        Extract technical metadata from a video file.
        This metadata helps establish video documentation patterns and archival qualities.

        Args:
            video_path (Path): Path to the video file to analyze.

        Returns:
            dict: Technical metadata including dimensions, framerate and duration.
            None: If video metadata cannot be extracted.
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return None

            # Get basic properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            cap.release()

            return {
                "width": width,
                "height": height,
                "fps": fps,
                "duration": round(duration, 2)
            }
        except Exception as e:
            print(f"Error processing {video_path}: {str(e)}")
            return None

    def get_path_info(self, file_path):
        """
        Infer hyperobject categorical and spatial orientation information from file location.
        This helps build the hierarchical relationships in the hyperobject ontology.
        
        The function works by:
        1. Converting the full path to a path relative to the root directory
        2. Analyzing path components to find orientation markers ('hor' or 'ver')
        3. Identifying the category from the first non-orientation folder name
        
        For example, given path "root/mineria/hor/video.mp4":
        - Category would be "mineria" 
        - Orientation would be "hor"

        Args:
            file_path (Path): Path to analyze for ontological classification.
                            Should be a Path object pointing to a video file.

        Returns:
            tuple: A tuple containing:
                  - category (str): The video's category based on folder structure
                  - orientation (str): The spatial orientation ('hor'/'ver') if found,
                                     None if no orientation marker present
        """
        # Convert path to relative path from root_dir
        rel_path = file_path.relative_to(self.root_dir)
        parts = rel_path.parts
        
        # Find orientation
        orientation = next((part.lower() for part in parts 
                          if self.orientation_patterns.match(part)), None)[:3]
        
        # Get category (first folder that's not an orientation folder)
        category = next((part for part in parts 
                        if not self.orientation_patterns.match(part)), None)
        
        return category, orientation

    def process_video_file(self, file_path):
        """
        Build a complete hyperobject ontological entry for a video by analyzing its metadata and location.
        
        The function performs the following steps:
        1. Validates the file is an MP4 video
        2. Extracts technical metadata like dimensions, framerate and duration using OpenCV
        3. Analyzes the file path to determine category and orientation based on folder structure
        4. Determines video type (animated or text) based on filename patterns
        5. Combines all information into a standardized ontology entry
        
        The resulting entry contains:
        - name: Original filename
        - path: Relative path from root directory
        - category: Classification based on folder structure
        - orientation: Spatial orientation (horizontal/vertical) if specified
        - video_type: Type of video (animated or text)
        - width: Video width in pixels
        - height: Video height in pixels 
        - fps: Frames per second
        - duration: Length in seconds

        Args:
            file_path (Path): Path to the video file to analyze and index

        Returns:
            dict: Complete hyperobject ontological information for the video with all metadata
                 and classification properties
            None: If video is invalid or cannot be processed
        """
        if not str(file_path).lower().endswith('.mp4'):
            return None

        metadata = self.get_video_metadata(file_path)
        if not metadata:
            return None

        category, orientation = self.get_path_info(file_path)
        
        # Determine video type based on filename
        filename = file_path.name.lower()
        video_type = "animated" if ("gen" in filename or "ghq5" in filename) else "text"
        
        return {
            "name": file_path.name,
            "path": str(self.root_dir) + '/' + str(file_path.relative_to(self.root_dir)),
            "category": category,
            "orientation": orientation,
            "video_type": video_type,
            **metadata
        }

    def scan_directory(self):
        """
        Recursively scan the archive to build the complete hyperobject video ontology.
        Maps all valid video documentation and their relationships into the database.
        """
        for file_path in self.root_dir.rglob('*.mp4'):
            # Skip if file doesn't contain 'hor' AND doesn't contain 'rotated'
            if ('hor' not in str(file_path).lower()) and ('rotated' not in str(file_path).lower()):
                continue
            video_data = self.process_video_file(file_path)
            if video_data:
                self.database.append(video_data)

    def save_database(self, output_file='ontology_map.json'):
        """
        Persist the indexed hyperobject video ontology to a JSON file.
        The resulting map captures the full structure and metadata of the video archive.

        Args:
            output_file (str): Path where the ontology index will be saved. Defaults to 'ontology_map.json'.
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, indent=4, ensure_ascii=False)

def main():
    """
    Entry point for generating a complete ontological index of hyperobject video archives.
    Scans videos, infers hyperobject relationships and structure, and saves the resulting ontology.
    """
    mapper = VideoOntologyMapper()
    print("Scanning videos...")
    mapper.scan_directory()
    print(f"Found {len(mapper.database)} videos")
    mapper.save_database()
    print("Database saved to ontology_map.json")

if __name__ == "__main__":
    main() 