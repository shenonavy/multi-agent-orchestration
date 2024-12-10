from functools import lru_cache
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"postgresql://{os.getenv('POSTGRES_USER', 'insurance_user')}:{os.getenv('POSTGRES_PASSWORD', 'insurance_password')}@localhost:5432/{os.getenv('POSTGRES_DB', 'insurance_db')}"
    )
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

@lru_cache()
def get_settings():
    return Settings()
