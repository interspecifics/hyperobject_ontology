import json
from collections import defaultdict
from typing import Dict, List
import statistics

class OntologyCartographer:
    def __init__(self, json_file='ontology_map.json'):
        """Initialize cartographer with ontology data"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.categories = self._organize_by_category()

    def _organize_by_category(self) -> Dict:
        """Organize videos by category with orientation stats"""
        categories = defaultdict(lambda: {
            'videos': [],
            'orientations': defaultdict(list),
            'total_duration': 0,
            'count': 0
        })
        
        for video in self.data:
            category = video.get('category', 'uncategorized')
            orientation = video.get('orientation', 'unknown')
            
            categories[category]['videos'].append(video)
            categories[category]['orientations'][orientation].append(video)
            categories[category]['total_duration'] += video.get('duration', 0)
            categories[category]['count'] += 1
            
        return categories

    def get_category_stats(self, category_data: Dict) -> Dict:
        """Calculate statistics for a category"""
        stats = {
            'total_videos': category_data['count'],
            'total_duration': round(category_data['total_duration'], 2),
            'mean_duration': round(statistics.mean(
                video.get('duration', 0) for video in category_data['videos']
            ), 2),
            'orientations': {
                orient: len(videos)
                for orient, videos in category_data['orientations'].items()
            }
        }
        return stats

    def print_tree(self, output_file='cartography_diagram.txt'):
        """Print the ontology tree with statistics and save to file"""
        # Build the output string
        output = []
        output.append("\n=== HYPEROBJECT VIDEO ONTOLOGY MAP ===\n")
        
        # Total collection statistics
        total_videos = sum(cat['count'] for cat in self.categories.values())
        total_duration = sum(cat['total_duration'] for cat in self.categories.values())
        
        output.append(f"Total Collection Statistics:")
        output.append(f"├── Total Videos: {total_videos}")
        output.append(f"└── Total Duration: {round(total_duration/60, 2)} minutes\n")
        
        # Category trees
        for category, data in sorted(self.categories.items()):
            stats = self.get_category_stats(data)
            
            # Category header
            output.append(f"📁 {category.upper()}")
            
            # Category statistics
            output.append(f"├── Videos: {stats['total_videos']}")
            output.append(f"├── Duration: {stats['total_duration']} seconds")
            output.append(f"├── Mean Duration: {stats['mean_duration']} seconds")
            
            # Orientation breakdown
            output.append("└── Orientations:")
            orientations = stats['orientations']
            for i, (orient, count) in enumerate(orientations.items(), 1):
                prefix = '    └──' if i == len(orientations) else '    ├──'
                output.append(f"{prefix} {orient}: {count} videos")
            
            output.append("")  # Empty line between categories
        
        # Join all lines and print to console
        output_text = '\n'.join(output)
        print(output_text)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)

def main():
    try:
        cartographer = OntologyCartographer()
        cartographer.print_tree()
    except FileNotFoundError:
        print("Error: ontology_map.json not found. Please run ontology_maper.py first.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON file. Please check ontology_map.json format.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 