# celeryconfig.py
from celery import Celery
from celery.signals import worker_ready
import os

# Broker settings
broker_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
result_backend = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Redis connection settings
broker_connection_retry = True
broker_connection_retry_on_startup = True
broker_connection_max_retries = None
broker_pool_limit = 10
redis_max_connections = 20
broker_transport_options = {
    'visibility_timeout': 3600,  # 1 hour
    'socket_timeout': 300,       # 5 minutes
    'socket_connect_timeout': 30,  # 30 seconds
}

# Worker settings
worker_concurrency = 2
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 100
worker_cancel_long_running_tasks_on_connection_loss = True

# Task settings
task_acks_late = True
task_reject_on_worker_lost = True
task_time_limit = 3600  # 1 hour
task_soft_time_limit = 3300  # 55 minutes

# Health check
@worker_ready.connect
def worker_ready(**kwargs):
    print('Celery worker is ready!')

app = Celery('tasks')
app.config_from_object('celeryconfig')