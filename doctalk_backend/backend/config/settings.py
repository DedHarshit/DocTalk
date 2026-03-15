from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    CHROMA_DB_PATH: str = "./db/chroma_db"
    COLLECTION_NAME: str = "medicine_knowledge"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
