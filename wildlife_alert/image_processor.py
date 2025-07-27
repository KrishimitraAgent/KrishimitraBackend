import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize Gemini client using Vertex AI
client = genai.Client(
    vertexai=True,
    project='local-disk-467109-b9',
    location='us-central1'
)

class ImageProcessor:
    def __init__(self):
        self.target_animals = ["boar", "leopard", "lion"]

    def process_image(self, image_path: str) -> list[dict]:
        """
        Sends the image to Gemini for analysis and parses result for:
        - Animal name
        - Confidence level
        - Recommendation
        Returns a list with detection info or empty if no target animal is found.
        """
        try:
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()

            print(f"Sending image to Gemini for analysis: {image_path}")

            image_blob = {
                "mimeType": "image/jpeg",
                "data": image_bytes
            }

            prompt_text = (
                "Analyze this image for wildlife. "
                "Specifically, is there a boar, leopard, or lion present? "
                "If one of these animals is clearly visible, identify it. "
                "Also, estimate your confidence in the identification as a percentage (e.g., 95%). "
                "If none of these specific animals are present but other animals are, mention them. "
                "If no animals are present, state 'empty field'. "
                "Format your answer concisely: 'Animal: [Name], Confidence: [X]%' or 'Empty Field' or 'Other Animal: [Name]'. "
                "If it's a threat animal, add 'Recommendation: [Advice]'."
            )

            payload = types.Content(
                role="user",
                parts=[
                    types.Part(inline_data=image_blob),
                    types.Part(text=prompt_text)
                ]
            )

            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=payload
            )

            gemini_text_response = response.text.strip()
            print(f"Gemini Vision Raw Response: {gemini_text_response}")

            # Match response patterns
            animal_match = re.search(r"Animal:\s*(.+?)[,\n\r]+.*Confidence:\s*(\d+)%", gemini_text_response, re.IGNORECASE)
            recommendation_match = re.search(r"Recommendation:\s*(.+)", gemini_text_response, re.IGNORECASE)

            if animal_match:
                animal_type = animal_match.group(1).strip().lower()
                confidence = float(animal_match.group(2)) / 100.0
                recommendation = recommendation_match.group(1).strip() if recommendation_match else "No recommendation provided."

                result = {
                    "label": animal_type,
                    "confidence": confidence,
                    "recommendation": recommendation
                }

                if animal_type in self.target_animals and confidence >= 0.5:
                    print(f"✅ Target animal {animal_type} detected with high confidence.")
                else:
                    print(f"⚠️ Non-target or low-confidence animal detected: {animal_type} ({confidence*100:.1f}%)")
                return [result]

            elif "empty field" in gemini_text_response.lower():
                print("🟢 Gemini detected an empty field.")
                return []

            elif "other animal" in gemini_text_response.lower():
                other_match = re.search(r"Other Animal:\s*(\w+)", gemini_text_response, re.IGNORECASE)
                other_animal = other_match.group(1).strip().lower() if other_match else "unknown"
                return [{
                    "label": other_animal,
                    "confidence": 0.5,
                    "recommendation": "No recommendation provided."
                }]

            else:
                print("❌ Could not parse a valid animal response.")
                return []

        except FileNotFoundError:
            print(f"❌ Error: Image file not found at {image_path}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error processing image {image_path}: {e}")
            return []

