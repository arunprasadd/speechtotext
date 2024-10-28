# backend/app/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Dict, Set

class Settings(BaseSettings):
    # Base settings
    PROJECT_NAME: str = "Speech to Text Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Auth
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@db:5432/whisperdb"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # File Upload
    UPLOAD_DIR: Path = Path("/app/uploads")
    RECORDINGS_DIR: Path = Path("/app/uploads/recordings")
    MAX_FILE_SIZE: int = 100_000_000  # 100MB
    ALLOWED_EXTENSIONS: Set[str] = {"mp3", "wav", "mp4", "avi", "mov"}
    CHUNK_SIZE: int = 8192
        # Optimize for 4 vCPUs
    WORKERS_PER_CORE: int = 2
    MAX_WORKERS: int = 8
    
    # Celery settings
    CELERY_WORKER_CONCURRENCY: int = 3
    CELERY_MAX_TASKS_PER_CHILD: int = 100
    # Audio Recording
    MAX_RECORDING_DURATION: int = 300  # 5 minutes
    SAMPLE_RATE: int = 16000
    
    # Whisper Models
    WHISPER_MODELS: Dict[str, Dict] = {
        "tiny": {
            "name": "tiny",
            "accuracy": "Lowest",
            "speed": "Fastest",
            "memory": "~1GB"
        },
        "base": {
            "name": "base",
            "accuracy": "Basic",
            "speed": "Fast",
            "memory": "~1GB"
        },
        "small": {
            "name": "small",
            "accuracy": "Good",
            "speed": "Moderate",
            "memory": "~2GB"
        },
        "medium": {
            "name": "medium",
            "accuracy": "Better",
            "speed": "Slow",
            "memory": "~5GB"
        },
        "large": {
            "name": "large",
            "accuracy": "Best",
            "speed": "Slowest",
            "memory": "~10GB"
        }
    }
    
    # Supported Languages
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ja": "Japanese",
        "zh": "Chinese",
        "hi": "Hindi"
    }

    class Config:
        case_sensitive = True

settings = Settings()