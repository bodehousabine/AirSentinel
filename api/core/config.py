from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List, Optional
import json

class Settings(BaseSettings):
    # Application
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8501", "https://airsentinel.onrender.com"]
    
    # Dataset et ML
    DATASET_PATH: str = "data/processed/airsentinel_dataset.csv"
    ML_MODELS_PATH: str = "models/"

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # Supabase Storage
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
