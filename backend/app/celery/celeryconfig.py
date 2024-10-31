# backend/app/celery/celeryconfig.py
import os

# Broker and Backend URLs
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Redis settings
broker_transport_options = {
    'visibility_timeout': 3600,
    'max_connections': 20,
    'socket_timeout': 300,
    'socket_connect_timeout': 30,
}

result_backend_transport_options = {
    'retry_on_timeout': True
}

# Task settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
task_time_limit = 3600
task_soft_time_limit = 3300
worker_max_tasks_per_child = 100
worker_prefetch_multiplier = 1

# Retry settings
broker_connection_retry = True
broker_connection_retry_on_startup = True
broker_connection_max_retries = None

# Worker settings
worker_concurrency = 2
worker_lost_wait = 60

# Task result settings
task_ignore_result = False
task_track_started = True
task_reject_on_worker_lost = True
task_acks_late = True