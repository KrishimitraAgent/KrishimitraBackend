from google.adk.agents import LlmAgent
from .tools import store_crop_analysis

crop_doctor = LlmAgent(
    name="crop_disease_agent",
    model="gemini-2.5-pro",
    description=(
        "Receives an image of a diseased crop and returns both "
        "the disease name and actionable treatment recommendations."
    ),
    instruction=(
        "You are an agricultural expert. "
        "The user will upload a crop image. "
        "1. Identify the disease and give concise, actionable treatment advice. "
        "2. Return ONLY that plain text, no JSON or markdown. "
        "3. Call store_crop_analysis with the exact text. "
        "4. IMMEDIATELY exit the conversation afterwards."
    ),
    tools=[store_crop_analysis]
)