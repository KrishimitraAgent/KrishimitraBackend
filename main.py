from fastapi import FastAPI
from pydantic import BaseModel
from google.genai import types
from session_service import SessionService
from config import Settings
from google.adk.runners import Runner
from agent import coordinator
from dotenv import load_dotenv

load_dotenv()

app_config = Settings()

app = FastAPI(
    title="My Basic FastAPI App",
    description="A simple boilerplate for a FastAPI application.",
    docs_url="/documentation"
)

service =  SessionService()
session_service = service.session_service


coordinator_runner = Runner(
    agent=coordinator,
    session_service=session_service,
    app_name=app_config.APP_NAME
)

class CoordinatorRequest(BaseModel):
    input_message: str
    session_id:str
    user_id:str


@app.post("/chat", summary="Chat Endpoint")
async def call_agent(request: CoordinatorRequest):
    """Calls the Farming coordinator agent"""
    user_content = types.Content(role="user", parts=[types.Part(text=request.input_message)])
    final_response = "No Final Response Recieved yet"
    if await service.get_session(request.user_id, request.session_id) is None:
        await service.create_session(session_id=request.session_id, user_id=request.user_id)
    async for event in coordinator_runner.run_async(user_id=request.user_id, session_id=request.session_id, new_message=user_content):
        # print(f"Event: {event.type}, Author: {event.author}") # Uncomment for detailed logging
        if event.is_final_response() and event.content and event.content.parts:
            # For output_schema, the content is the JSON string itself
            final_response_content = event.content.parts[0].text
            print(final_response_content)

    return final_response_content


    # current_session = session_service.get_session(app_name=app_config.APP_NAME,
    #                                               user_id=request.user_id,
    #                                               session_id=request.ses)
    # stored_output = current_session.state.get(app_config.COORDINATOR_MODEL_OUTPUT_KEY)

    # # Pretty print if the stored output looks like JSON (likely from output_schema)
    # print(f"--- Session State ['{app_config.COORDINATOR_MODEL_OUTPUT_KEY}']: ", end="")


