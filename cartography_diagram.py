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
        # Calculate total duration for each orientation
        orientation_durations = {
            orient: sum(video.get('duration', 0) for video in videos)
            for orient, videos in category_data['orientations'].items()
        }
        
        # Calculate duration stats (min, mean, max)
        durations = [video.get('duration', 0) for video in category_data['videos']]
        duration_stats = (
            round(min(durations), 2),
            round(statistics.mean(durations), 2),
            round(max(durations), 2)
        ) if durations else (0, 0, 0)
        
        stats = {
            'total_videos': category_data['count'],
            'total_duration': round(category_data['total_duration'], 2),
            'total_duration_min': round(category_data['total_duration'] / 60, 2),
            'duration_stats': duration_stats,
            'orientations': {
                orient: {
                    'count': len(videos),
                    'duration_sec': round(orientation_durations[orient], 2),
                    'duration_min': round(orientation_durations[orient] / 60, 2)
                }
                for orient, videos in category_data['orientations'].items()
            }
        }
        return stats

    def print_tree(self, output_file='cartography_diagram.txt'):
        """Print the ontology tree with statistics and save to file"""
        # Add ANSI escape codes for white background with black text
        HIGHLIGHT = '\033[7m'  # or alternatively: '\033[40;107m' for explicit black text on white background
        RESET = '\033[0m'
        
        # Build the output
        output = []
        output.append(f"\n=== {HIGHLIGHT}HYPEROBJECT VIDEO ONTOLOGY MAP{RESET} ===\n")
        
        # Total collection statistics
        total_videos = sum(cat['count'] for cat in self.categories.values())
        total_duration = sum(cat['total_duration'] for cat in self.categories.values())
        
        output.append(f"{HIGHLIGHT}Total Collection Statistics:{RESET}")
        output.append(f"├── Total Videos: {total_videos}")
        output.append(f"└── Total Duration: {round(total_duration/60, 2)} minutes\n")
        
        # Category trees
        for category, data in sorted(self.categories.items()):
            stats = self.get_category_stats(data)
            
            # Category header with highlighted text
            import random
            emojis = "❂❈※❅❇✿✴︎"
            output.append(f"{random.choice(emojis)} {HIGHLIGHT}{category.upper()}{RESET}")
            
            # Rest of the category statistics remain the same
            output.append(f"├── Videos: {stats['total_videos']}")
            output.append(f"├── Duration: {stats['total_duration']} seconds ({stats['total_duration_min']} minutes)")
            output.append(f"├── Duration Min/Mean/Max: {stats['duration_stats']} seconds")
            
            output.append("└── Orientations:")
            orientations = stats['orientations']
            for i, (orient, orient_stats) in enumerate(orientations.items(), 1):
                prefix = '    └──' if i == len(orientations) else '    ├──'
                output.append(f"{prefix} {orient}: {orient_stats['count']} videos ({orient_stats['duration_min']} minutes)")
            
            output.append("")
        
        # Join all lines
        output_text = '\n'.join(output)
        
        # Print to console with ANSI codes
        print(output_text)
        
        # Save to file without ANSI codes (clean version)
        clean_text = output_text.replace(HIGHLIGHT, '').replace(RESET, '')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_text)

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