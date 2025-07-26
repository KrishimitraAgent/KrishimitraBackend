from google.adk.agents import LlmAgent
from greetor import greetor_agent





coordinator = LlmAgent(
    name="farming_coordinator",
    description="A coordinator agent for farming tasks",
    instruction="You are farming Assisntant. Delegate the greetings to greetor_agent",
    model="gemini-2.0-flash",
    sub_agents=[greetor_agent]
)

