from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    VERSION: str
    API_PREFIX: str
    DEBUG: bool
    POSTGRESQL_URL: str
    SECRET_KEY: str
    ALGORITHM_TOKEN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    API_KEY: str

settings = Settings(
    PROJECT_NAME="Task Management API",
    PROJECT_DESCRIPTION="API para gestión de tareas y usuarios",
    VERSION="0.1.0",
    API_PREFIX="/api/v1",
    DEBUG=True,
    API_KEY = os.getenv("API_KEY"),
    POSTGRESQL_URL=os.getenv("POSTGRESQL_URL"),
    SECRET_KEY = os.getenv("SECRET_KEY"),
    ALGORITHM_TOKEN = os.getenv("ALGORITHM"),
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
    
)