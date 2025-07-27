from coordinator_agent.agent import root_agent

import vertexai

PROJECT_ID = "local-disk-467109-b9"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://adk_stage_bucket"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

from vertexai import agent_engines

remote_agent = agent_engines.create(
    app,
    requirements=[
        "google-cloud-aiplatform[agent_engines,adk]",
        "google-adk",
        "fastapi",
        "uvicorn",
        "vertexai",
        "google-cloud-firestore",
        "google-cloud-storage"
    ],
    extra_packages = [
        "coordinator_agent", 
        "cropprice_agent", 
        "greetor",
        "crop_doctor",
        "farmer_mood"
    ],
    gcs_dir_name = None,
    display_name="Farming Coordinator Agent",
    description="A coordinator agent for farming tasks that delegates greetings and crop price queries.",
)