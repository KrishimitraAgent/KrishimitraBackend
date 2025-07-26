from google.adk.sessions import InMemorySessionService
from config import Settings

app_config = Settings()

class SessionService:
    def __init__(self):
        self.session_service = InMemorySessionService()

    def get_session(self, user_id: str, session_id:str):
        """Retrieve a session by its ID."""
        return self.session_service.get_session(app_name=app_config.APP_NAME,user_id=user_id, session_id=session_id)
    
    def create_session(self, session_id: str, user_id: str):
        """Create a new session with the given ID and user ID."""
        return self.session_service.create_session(app_name=app_config.APP_NAME, session_id= session_id, user_id=user_id)