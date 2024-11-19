# hyperobject_ontology

tools for analyzing, cataloging, and describing video collections through the lens of hyperobject ontologies. This project helps organize and understand video documentation of hyperobjects by creating structured ontologies with generative descriptions.

## Overview

The project consists of several tools that work together to:
1. Map and extract metadata from video files in a structured directory
2. Generate a cartographic diagram of the video collection
3. Generate descriptions using GPT-4o vision model
4. Organize videos by hyperobject categories and spatial orientations

## Components

### Core Scripts

- `ontology_map.py`: Creates a structured JSON database of video files by:
  - Scanning the Generados directory recursively
  - Extracting video metadata (dimensions, duration, fps)
  - Organizing files by category and orientation (Hor/Ver)
  - Saving complete metadata to ontology_map.json

- `cartography_diagram.py`: Generates a cartography diagram by:
  - Organizing videos by categories and orientations
  - Computing total and mean video durations per category
  - Generating detailed orientation breakdowns
  - Creating ASCII tree diagrams with random decorative symbols
  - Displaying total collection statistics (video count and duration)
  - Saving human-readable visualizations to cartography_diagram.txt

- `hyperobject_annotator.py`: Augments the ontology metadata with generative descriptions by:
  - Extracting middle frames from videos
  - Using GPT-4o for visual analysis
  - Generating contextual descriptions
  - Saving progress incrementally to annotated_ontology.json

### Output Files

- `ontology_map.json`: Primary database containing:
  - Video metadata (name, path, dimensions, duration)
  - Category classifications
  - Orientation information

- `annotated_ontology.json`: Enhanced database including:
  - All metadata from ontology_map.json
  - Generated descriptions ('texto' field)
  - Incremental updates as processing continues

- `cartography_diagram.txt`:  Visualization showing:
  - Total collection metrics
  - Per-category breakdowns
  - Orientation distributions
  - Duration statistics

## Installation

1. Clone the repository
2. Install dependencies:


