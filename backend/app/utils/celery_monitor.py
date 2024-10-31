# backend/app/utils/celery_monitor.py
from app.celery import celery_app
import logging

logger = logging.getLogger(__name__)

def check_celery_workers():
    """Check active Celery workers"""
    try:
        insp = celery_app.control.inspect()
        active_workers = insp.active()
        if active_workers:
            logger.info(f"Active workers: {active_workers}")
            return True
        logger.error("No active workers found")
        return False
    except Exception as e:
        logger.error(f"Error checking workers: {str(e)}")
        return False

def monitor_task_status(task_id: str):
    """Monitor task status"""
    try:
        result = celery_app.AsyncResult(task_id)
        logger.info(f"Task {task_id} status: {result.status}")
        return result.status
    except Exception as e:
        logger.error(f"Error monitoring task: {str(e)}")
        return None