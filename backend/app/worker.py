# backend/app/worker.py
from celery import Celery
from .config import settings

celery = Celery(
    "whisper_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_max_memory_per_child=1000000,  # 1GB
    worker_prefetch_multiplier=1
)

# Optional: Configure task routes
celery.conf.task_routes = {
    "app.tasks.transcribe_audio": {"queue": "transcription"},
    "app.tasks.process_recording": {"queue": "recording"}
}