# backend/app/worker.py
from celery import Celery
from .config import settings

celery = Celery(
    'tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks']
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_max_memory_per_child=1000000,
    worker_prefetch_multiplier=1,
    broker_transport_options={'visibility_timeout': 3600},
    broker_connection_retry=True,
    broker_connection_max_retries=None
)