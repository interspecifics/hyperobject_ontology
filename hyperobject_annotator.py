import json
import cv2
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import base64
from tqdm import tqdm

load_dotenv()

class HyperobjectAnnotator:
    def __init__(self, ontology_file='ontology_map.json', output_file='annotated_ontology.json'):
        """Initialize the annotator with OpenAI client and load ontology"""
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.output_file = output_file
        
        # Load existing annotations if they exist
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                self.ontology = json.load(f)
                print(f"Loaded {len(self.ontology)} existing annotations")
        else:
            # Load fresh ontology if no annotations exist
            with open(ontology_file, 'r', encoding='utf-8') as f:
                self.ontology = json.load(f)
            
        self.root_dir = Path("Generados")

    def extract_middle_frame(self, video_path):
        """Extract a frame from the middle of the video"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return None
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            middle_frame = total_frames // 2
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            ret, frame = cap.read()
            
            if ret:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    return base64.b64encode(buffer).decode('utf-8')
            
            return None
        except Exception as e:
            print(f"Error extracting frame: {str(e)}")
            return None
        finally:
            cap.release()

    def get_hyperobject_description(self, base64_image, video_data):
        """Generate description using GPT-4o"""
        try:
            prompt = f"""
            Observa los presentes en esta imagen.

            Genera una descripción que:
            1. Identifique y describa objetos, formas o elementos específicos visibles en la imagen
            2. Presente estos elementos de manera difusa o creativa, sugiriendo múltiples interpretaciones posibles
            3. Mantenga un balance entre lo concreto de los elementos observados y lo difuso de su interpretación, relacionándolo con la categoría '{video_data.get('category', 'desconocida')}'
            
            No hagas mención de la imagen solo escribe la idea.
            """

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=8000,
                temperature=1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating description: {str(e)}")
            return None

    def save_current_progress(self):
        """Save current state of ontology"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.ontology, f, indent=4, ensure_ascii=False)

    def annotate_ontology(self):
        """Process videos and add GPT-4o generated descriptions"""
        print("Starting annotation process with GPT-4o...")
        
        # Filter out already annotated videos
        to_process = [video for video in self.ontology if 'texto' not in video]
        
        if not to_process:
            print("All videos have been annotated!")
            return
            
        print(f"Found {len(to_process)} videos to process")
        
        for video_data in tqdm(to_process, desc="Annotating videos"):
            video_path = self.root_dir / video_data['path']
            
            base64_image = self.extract_middle_frame(video_path)
            if not base64_image:
                print(f"Could not extract frame from {video_path}")
                continue
                
            description = self.get_hyperobject_description(base64_image, video_data)
            if description:
                # Find the video in the main ontology and update it
                for video in self.ontology:
                    if video['path'] == video_data['path']:
                        video['texto'] = description
                        break
                
                # Save progress after each successful annotation
                self.save_current_progress()
                print(f"\nProcessed: {video_data['path']}")
                print(f"Description: {description[:100]}...")

def main():
    try:
        annotator = HyperobjectAnnotator()
        annotator.annotate_ontology()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 