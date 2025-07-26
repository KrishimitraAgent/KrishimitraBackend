from google.adk.agents import LlmAgent
from .prompts import return_price_instructions
from .tools import call_price_api


cropprice_agent = LlmAgent(
    name="Crop_price_agent",
    description="Crop_price_agent",
    instruction=return_price_instructions(),
    model="gemini-2.5-pro",
    tools = [call_price_api]
)