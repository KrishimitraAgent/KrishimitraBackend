# main.py
import os
import sys
import time
from contextlib import asynccontextmanager
from threading import Thread # Import Thread for running the agent in a background thread

# Import FastAPI for the web application framework
from fastapi import FastAPI

# Import the custom modules
from agent import Agent
from firestore_utils import FirestoreUtils
from image_processor import ImageProcessor

# Import load_dotenv to ensure environment variables are loaded at startup
from dotenv import load_dotenv

# Load environment variables FIRST, before any other module tries to access them
load_dotenv()

# Define the folder where images will be monitored
IMAGE_FOLDER = "sample_images"

# Global variables to hold initialized instances, accessible across the app
# These will be initialized within the lifespan context
agent_instance: Agent | None = None
firestore_client_instance: FirestoreUtils | None = None
image_processor_instance: ImageProcessor | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for application startup and shutdown events.
    This is where the AI agent and its dependencies are initialized and the
    detection loop is started in a background thread.
    """
    global agent_instance, firestore_client_instance, image_processor_instance

    print("🚀 Starting Wildlife Protection AI Agent Application...")

    # Ensure the image folder exists
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    print(f"📂 Monitoring image folder: {IMAGE_FOLDER}")

    try:
        # 1. Initialize Firestore Utilities
        firestore_client_instance = FirestoreUtils()
        print("✅ Firestore Utilities initialized.")

        # 2. Initialize Image Processor (Gemini Vision)
        image_processor_instance = ImageProcessor()
        print("✅ Image Processor initialized (using Gemini Pro Vision).")

        # 3. Initialize the Main AI Agent
        # Pass the initialized utility objects to the Agent
        agent_instance = Agent(
            image_processor=image_processor_instance,
            firestore_utils=firestore_client_instance
        )
        print("✅ AI Agent initialized.")

        # 4. Start detection loop in a background thread
        # This prevents the agent's blocking loop from freezing the FastAPI server
        def run_agent_loop_in_background():
            """Wrapper function to run the agent's detection loop."""
            try:
                agent_instance.run_detection_loop(image_source_dir=IMAGE_FOLDER, detection_interval_sec=5)
            except Exception as e:
                print(f"agent loop:")
                

       
        agent_thread = Thread(target=run_agent_loop_in_background, daemon=True)
        agent_thread.start()
        print("🧠 AI Agent monitoring started in background thread.")

        # Yield control to FastAPI to start serving requests
        yield

        # --- Application Shutdown (code after yield will run on shutdown) ---
        print("🛑 Shutting down AI Agent and FastAPI application...")
        # Add any cleanup logic here if necessary (e.g., stopping threads gracefully)

    except EnvironmentError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please ensure your .env file is correctly set up with GEMINI_API_KEY and FIRESTORE_CREDENTIALS_PATH.")
        # Re-raise the exception to prevent FastAPI from starting
        raise
    except Exception as e:
        print(f"❌ Unrecoverable startup error: {e}")
        # Re-raise the exception to prevent FastAPI from starting
        raise

# Create FastAPI app instance, linking it to the lifespan context manager
app = FastAPI(lifespan=lifespan)

# Example API route (you can add more here for interacting with the agent or data)
@app.get("/")
async def root():
    """
    Root endpoint for the FastAPI application.
    Returns a simple status message.
    """
    return {"message": "Wildlife Protection AI Agent is running 🐾"}

# You can add more API endpoints here, for example, to manually trigger a scan,
# retrieve detection history, or update agent settings.
# Example:
# @app.get("/status")
# async def get_status():
#     # You can return information about the agent's current state,
#     # like last detection time, number of alerts, etc.
#     return {"agent_status": "running", "last_detection": "..."}