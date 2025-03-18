from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

def get_url_database(name) -> str:
    return f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{name}"

class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    VERSION: str
    API_PREFIX: str
    DEBUG: bool
    POSTGRESQL_URL: str
    POSTGRESQL_URL_TEST: str= "" 
    POSTGRESQL_URL_ADMIN: str
    POSTGRESQL_DATABASE_NAME_TEST: str  
    SECRET_KEY: str
    ALGORITHM_TOKEN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    API_KEY: str
    
    def model_post_init(self, __context):
        self.POSTGRESQL_URL_TEST = get_url_database(self.POSTGRESQL_DATABASE_NAME_TEST)
    
settings = Settings(
    PROJECT_NAME="Task Management API",
    PROJECT_DESCRIPTION="API para gestión de tareas y usuarios",
    VERSION="0.1.0",
    API_PREFIX="/api/v1",
    DEBUG=True,
    API_KEY=os.getenv("API_KEY"),
    POSTGRESQL_URL=get_url_database(os.getenv("POSTGRES_DATABASE")),
    SECRET_KEY=os.getenv("SECRET_KEY"),
    ALGORITHM_TOKEN=os.getenv("ALGORITHM"),
    ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"),
    POSTGRESQL_DATABASE_NAME_TEST=f"test_db_{uuid.uuid4().hex[:10]}",
    POSTGRESQL_URL_ADMIN=get_url_database('postgres')
)



    