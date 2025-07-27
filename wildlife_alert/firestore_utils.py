# firestore_utils.py
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FirestoreUtils:
    def __init__(self):
        # Get Firestore credentials path from environment variable
        cred_path = os.getenv("FIRESTORE_CREDENTIALS_PATH")
        if not cred_path:
            raise ValueError("FIRESTORE_CREDENTIALS_PATH not set in .env file.")

        # Initialize Firebase Admin SDK only once
        # This check prevents re-initialization if the class is instantiated multiple times
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized successfully.")
            except Exception as e:
                print(f"Error initializing Firebase Admin SDK: {e}")
                raise
        self.db = firestore.client()

    def log_detection(self, detection_data: dict):
        """
        Logs a detailed wildlife detection event to the 'detections' collection in Firestore.
        
        Args:
            detection_data (dict): A dictionary containing details about the detection,
                                   e.g., {"animal_type": "boar", "confidence": 0.95, 
                                         "bounding_box": [x1, y1, x2, y2], "image_filename": "boar_001.jpg"}
        """
        try:
            detections_ref = self.db.collection('detections')
            detections_ref.add({
                "timestamp": firestore.SERVER_TIMESTAMP, # Use server timestamp for accuracy
                **detection_data # Unpack the detection_data dictionary
            })
            print(f"✅ Logged detection to Firestore: {detection_data.get('animal_type', 'Unknown')} at server timestamp.")
        except Exception as e:
            print(f"❌ Error logging detection to Firestore: {e}")

    def send_realtime_alert(self, alert_data: dict):
        """
        Sends a real-time alert to the 'alerts' collection in Firestore.
        This is for immediate notifications that a listener can pick up.

        Args:
            alert_data (dict): A dictionary containing alert-specific information,
                               e.g., {"type": "animal_threat", "animal": "leopard",
                                     "message": "URGENT: Leopard detected!", "image_ref": "leopard_field.jpg"}
        """
        try:
            alerts_ref = self.db.collection('alerts')
            alerts_ref.add({
                "timestamp": firestore.SERVER_TIMESTAMP, # Use server timestamp for accuracy
                "status": "new", # A status field can be useful for client-side processing (e.g., mark as 'read')
                **alert_data # Unpack the alert_data dictionary
            })
            print(f"🚨 Sent real-time alert to Firestore: {alert_data.get('message', 'No message')}")
        except Exception as e:
            print(f"❌ Error sending real-time alert to Firestore: {e}")

# Note: The `db = init_firestore()` and `log_alert()` functions from your original
# file are now encapsulated within the FirestoreUtils class.
# You will instantiate this class in `agent.py` or `main.py`.
# Example usage (in another file like agent.py or main.py):
# from firestore_utils import FirestoreUtils
# firestore_client = FirestoreUtils()
# firestore_client.log_detection({"animal_type": "boar", "confidence": 0.99, "bounding_box": [10,20,30,40], "image_filename": "test.jpg"})
# firestore_client.send_realtime_alert({"type": "threat", "animal": "lion", "message": "Lion spotted!", "image_ref": "lion_test.jpg"})