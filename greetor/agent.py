from google.adk.agents import LlmAgent


greetor_agent = LlmAgent(
    name="greetor",
    description="Greetor",
    instruction="Greet the users",
    model="gemini-2.0-flash"
)