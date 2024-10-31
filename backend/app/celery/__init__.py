# backend/app/celery/__init__.py
from celery import Celery

celery_app = Celery('tasks')
celery_app.config_from_object('app.celery.celeryconfig')

# Import tasks here
from .tasks import *  # Add this line

# Configure routes
celery_app.conf.task_routes = {
    'app.celery.tasks.*': {'queue': 'celery'}
}