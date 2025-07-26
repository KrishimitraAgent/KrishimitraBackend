from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str = "KRISHIMITRA"

    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GOOGLE_API_KEY: str ="AIzaSyDd15KZUMHdvOXQZ9-jTkhQQUGqT1DLdGw"

    COORDINATOR_MODEL: str = "TBD"

    COORDINATOR_MODEL_OUTPUT_KEY: str = "coordinator_output"


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")