from google.adk.agents import LlmAgent
from greetor import greetor_agent
from cropprice_agent import price_agent
from crop_doctor import crop_doctor
from farmer_mood import farmer_agent

root_agent = LlmAgent(
    name="farming_coordinator",
    description="A coordinator agent for farming tasks",
    instruction="You are farming Assisntant. Delegate the greetings to greetor_agent, Delegate the crop price related queries to price_agent, Delegate the crop disease related queries to crop_doctor, Delegate mental health queries related to farmer_mood",
    model="gemini-2.0-flash",
    sub_agents=[greetor_agent, price_agent, crop_doctor, farmer_agent]
)

