# agent.py
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

from firestore_utils import FirestoreUtils
from image_processor import ImageProcessor

load_dotenv() # It's good practice to have this here too for robustness

class Agent:
    # --- CHANGE START ---
    # The __init__ method MUST accept image_processor and firestore_utils
    def __init__(self, image_processor: ImageProcessor, firestore_utils: FirestoreUtils):
    # --- CHANGE END ---
        self.firestore_utils = firestore_utils  # <--- Assign the passed instance
        self.image_processor = image_processor  # <--- Assign the passed instance

        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # You're using 'gemini-pro' for text decisions, which is fine here.
        # The vision part is handled by image_processor.py's call to gemini-pro-vision.
        self.gemini_model = genai.GenerativeModel('gemini-pro')

        self.target_animals = ["boar", "leopard", "lion"]
        self.detection_confidence_threshold = 0.75

    def _get_gemini_decision(self, animal_type: str, confidence: float) -> str:
        """
        Uses Gemini API to get a recommended action based on detected animal and confidence.
        """
        prompt = f"""
        A wildlife detection system has identified a {animal_type} with a confidence of {confidence:.2f}.
        This system is protecting an agricultural field from target animals like boar, leopard, and lion.
        Based on this information, what immediate action should be taken?
        Possible actions: "ALERT_IMMEDIATELY", "MONITOR", "IGNORE".
        If it's a target animal with high confidence, recommend "ALERT_IMMEDIATELY".
        If it's a non-target animal or low confidence, recommend "MONITOR" or "IGNORE".
        Provide only the action word.
        """
        try:
            response = self.gemini_model.generate_content(prompt)
            decision = response.text.strip().upper()
            return decision
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return "MONITOR"

    def run_detection_loop(self, image_source_dir="sample_images", detection_interval_sec=5):
        """
        Main detection loop. Continuously monitors for images, processes them,
        and triggers actions based on detections.
        """
        print(f"Starting wildlife detection loop. Monitoring {image_source_dir}...")
        processed_images = set()

        while True:
            for filename in os.listdir(image_source_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and filename not in processed_images:
                    image_path = os.path.join(image_source_dir, filename)
                    print(f"\nProcessing image: {image_path}")

                    detections = self.image_processor.process_image(image_path)

                    if detections:
                        for detection in detections:
                            animal_type = detection["label"]
                            confidence = detection["confidence"]
                            bbox = detection["box"]

                            print(f"  Detected: {animal_type} (Confidence: {confidence:.2f}, Box: {bbox})")

                            self.firestore_utils.log_detection({
                                "image_filename": filename,
                                "animal_type": animal_type,
                                "confidence": confidence,
                                "bounding_box": bbox,
                                "source": "camera_feed_simulated"
                            })

                            if animal_type in self.target_animals and confidence >= self.detection_confidence_threshold:
                                print(f"  Target animal {animal_type} detected with high confidence. Querying Gemini for action...")
                                gemini_action = self._get_gemini_decision(animal_type, confidence)
                                print(f"  Gemini recommends: {gemini_action}")

                                if gemini_action == "ALERT_IMMEDIATELY":
                                    alert_message = f"URGENT: {animal_type.upper()} detected in the field! Confidence: {confidence:.2f}. Location: {image_path}"
                                    self.firestore_utils.send_realtime_alert({
                                        "type": "animal_threat",
                                        "animal": animal_type,
                                        "confidence": confidence,
                                        "message": alert_message,
                                        "image_ref": filename
                                    })
                                elif gemini_action == "MONITOR":
                                    print(f"  Monitoring {animal_type} situation.")
                            elif animal_type not in self.target_animals and confidence >= self.detection_confidence_threshold:
                                print(f"  Non-target animal {animal_type} detected. No immediate alert.")
                            else:
                                print(f"  Detection below confidence threshold or not a target animal for immediate action.")

                        processed_images.add(filename)

            time.sleep(detection_interval_sec)