# backend/app/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Dict, Set, Optional
import os

class Settings(BaseSettings):
    # Base settings
    PROJECT_NAME: str = "Speech to Text Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@db:5432/whisperdb"
    )
    
    # Redis and Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    
    # File Upload Settings
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
    RECORDINGS_DIR: Path = Path(os.getenv("RECORDINGS_DIR", "/app/uploads/recordings"))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100000000"))  # 100MB
    ALLOWED_EXTENSIONS: Set[str] = {"mp3", "wav", "mp4", "avi", "mov"}
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "8192"))
    
    # Server Settings
    WORKERS_PER_CORE: int = int(os.getenv("WORKERS_PER_CORE", "2"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "8"))
    
    # Celery Worker Settings
    CELERY_WORKER_CONCURRENCY: int = int(os.getenv("CELERY_WORKER_CONCURRENCY", "3"))
    CELERY_MAX_TASKS_PER_CHILD: int = int(os.getenv("CELERY_MAX_TASKS_PER_CHILD", "100"))
    CELERY_TASK_TIME_LIMIT: int = int(os.getenv("CELERY_TASK_TIME_LIMIT", "3600"))  # 1 hour
    CELERY_TASK_SOFT_TIME_LIMIT: int = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "3300"))  # 55 minutes
    
    # Recording Settings
    MAX_RECORDING_DURATION: int = int(os.getenv("MAX_RECORDING_DURATION", "300"))  # 5 minutes
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "16000"))
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = [
        "https://transcriptwithai.com",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Whisper Models
    WHISPER_MODELS: Dict[str, Dict] = {
        "tiny": {
            "name": "tiny",
            "accuracy": "Lowest",
            "speed": "Fastest",
            "memory": "~1GB",
            "max_file_size": 50_000_000  # 50MB
        },
        "base": {
            "name": "base",
            "accuracy": "Basic",
            "speed": "Fast",
            "memory": "~1GB",
            "max_file_size": 100_000_000  # 100MB
        },
        "small": {
            "name": "small",
            "accuracy": "Good",
            "speed": "Moderate",
            "memory": "~2GB",
            "max_file_size": 150_000_000  # 150MB
        },
        "medium": {
            "name": "medium",
            "accuracy": "Better",
            "speed": "Slow",
            "memory": "~5GB",
            "max_file_size": 200_000_000  # 200MB
        },
        "large": {
            "name": "large",
            "accuracy": "Best",
            "speed": "Slowest",
            "memory": "~10GB",
            "max_file_size": 300_000_000  # 300MB
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
        "hi": "Hindi",
        "auto": "Auto Detect"
    }

    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Cleanup Settings
    CLEANUP_INTERVAL_HOURS: int = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))
    FILE_RETENTION_DAYS: int = int(os.getenv("FILE_RETENTION_DAYS", "7"))

    def get_model_max_file_size(self, model_name: str) -> int:
        """Get maximum file size for a specific model"""
        return self.WHISPER_MODELS.get(model_name, {}).get('max_file_size', self.MAX_FILE_SIZE)

    def validate_file_extension(self, filename: str) -> bool:
        """Validate file extension"""
        return filename.lower().split('.')[-1] in self.ALLOWED_EXTENSIONS

    def validate_language_code(self, language_code: str) -> bool:
        """Validate language code"""
        return language_code in self.SUPPORTED_LANGUAGES

    def get_upload_path(self) -> Path:
        """Get upload directory path and ensure it exists"""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        return self.UPLOAD_DIR

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()