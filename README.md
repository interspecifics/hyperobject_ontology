# Hyperobject_ontology V.0 

El "hiperobjeto" fue propuesto por el filósofo Timothy Morton para describir ciertos fenómenos o entidades que son masivos, complejos y difíciles de comprender en su totalidad debido a su escala, extensión temporal o espacial. Un hiperobjeto no puede ser percibido o comprendido completamente en un solo instante o lugar, ya que su influencia se extiende más allá de nuestra capacidad de percepción inmediata.

Algunas características clave de los hiperobjetos incluyen:

1. Escala masiva: Los hiperobjetos abarcan vastas dimensiones de tiempo o espacio. No podemos verlos de manera total, ya que no se limitan a un solo lugar o momento.

2. No-localización: Aunque pueden tener efectos visibles en lugares específicos, los hiperobjetos no están confinados a un solo lugar. Su presencia y efectos se distribuyen ampliamente.

3. Persistencia temporal: Los hiperobjetos no tienen un ciclo de vida corto, sino que existen a lo largo de períodos muy largos, mucho más allá de la vida humana. Un ejemplo de esto es el cambio climático, que se despliega en escalas temporales que sobrepasan la percepción humana.

4. Impacto en la percepción humana: Los hiperobjetos desafían nuestras formas de entender el mundo, ya que nuestras capacidades cognitivas y sensoriales están limitadas para abordarlos en su totalidad.

Un ejemplo de hyperobjeto clave es la economía global, o actividad económica. Ver la economía como un hiperobjeto nos permite comprenderla como un sistema masivo, interconectado y persistente, cuyas interacciones y efectos van más allá de nuestra capacidad de percibir o controlar completamente. Esta visión implica reconocer la interdependencia global, el impacto a largo plazo de nuestras acciones económicas, y la necesidad de enfoques más holísticos y sostenibles para comprender y gestionar las dinámicas económicas en un mundo globalizado.

Hyperobject Ontology v.0  es un ensayo audiovisual, propuesto como una forma de pensar sobre la existencia y la naturaleza de los hiperobjetos, que son fenómenos o entidades extremadamente grandes, complejas y difíciles de comprender en su totalidad. En esta primera etapa de ontología buscamos proponer un forma de aproximación artistica que nos habilite a pensar como conceptualizamos, experimentamos y comprendemos objetos que desafían las categorías tradicionales de ser y existencia debido a su magnitud y la manera en que se distribuyen en el tiempo y el espacio.
Proponemos este ejercicio de ontología de los hiperobjetos para observar en conjunto cómo estos objetos "existen" y cómo afectan nuestra relación con ellos, dado que no pueden ser fácilmente percibidos o comprendidos, busca reflexionar sobre la naturaleza del ser de tales objetos su red de relaciones globales  y cómo pueden ser abordados en términos filosóficos, éticos y científicos, tomando como punto de partida para este primer ensayo la observación de la economía y sus relaciones. 



# Hyperobject_ontology tools 


tools for analyzing, cataloging, and describing video collections through the lens of hyperobject ontologies. This project helps organize and understand video documentation of hyperobjects by creating structured ontologies with generative descriptions.


🀨 [cartography diagram](cartography_diagram.txt)

🀦 [ontology map with hyperobject annotations](annotated_ontology.json)

## Overview

The repository consists of several tools that work together to:
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

- `ho_master.py`: Manages distributed video playback system (Work in Progress):
  - Creates a network of synchronized video players
  - Coordinates video playback across multiple displays
  - Handles tag-based video selection and distribution
  - Manages socket connections with slave players
  - Currently supports up to 3 slave displays

- `ho_slave.py`: Individual video player node (Work in Progress):
  - Receives video assignments from master node
  - Handles local video playback using pygame/ffpyplayer
  - Maintains unique ID for master-slave communication
  - Reads video metadata from videos.json
  - Manages display settings and video rendering

### ToDo

~~1. Video Metadata Enhancement:~~ (listo)
   - Add video duration metadata to the system
   - Implement duration tracking and synchronization

2. Tag-based Playback Logic:
   - Develop intelligent video selection based on tag relations
   - Update play_video function to handle tag-based selection
   - Implement video transition logic

3. Network Communication:
   - Improve master-slave synchronization
   - Add error handling for network disconnections
   - Implement reconnection logic

4. Display Configuration:
   - Update display resolution settings (currently 640x480, planned 1920x1080)
   - Add support for different aspect ratios
   - Implement multi-display coordination

### Output Files

- [ontology_map.json](ontology_map.json): Primary database containing:
  - Video metadata (name, path, dimensions, duration)
  - Category classifications
  - Orientation information

- [annotated_ontology.json](annotated_ontology.json): Enhanced database including:
  - All metadata from ontology_map.json
  - Generated descriptions ('texto' field)
  - Incremental updates as processing continues

- [cartography_diagram.txt](cartography_diagram.txt):  Visualization showing:
  - Total collection metrics
  - Per-category breakdowns
  - Orientation distributions
  - Duration statistics

## Installation

1. Clone the repository
2. Install dependencies:

