# backend/app/tasks.py
import logging
from celery import Task
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Transcription
from .utils.transcription import transcribe_audio
from .worker import celery

logger = logging.getLogger(__name__)

class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None

@celery.task(bind=True, base=DatabaseTask)
def transcribe_audio_task(
    self,
    transcription_id: int,
    model_size: str,
    language: str
):
    """Process transcription task"""
    logger.info(f"Starting transcription task {transcription_id}")
    
    try:
        # Get transcription from database
        transcription = self.db.query(Transcription).filter(
            Transcription.id == transcription_id
        ).first()

        if not transcription:
            logger.error(f"Transcription {transcription_id} not found")
            return {"status": "failed", "error": "Transcription not found"}

        # Update status to processing
        transcription.status = "processing"
        self.db.commit()

        # Transcribe audio
        logger.info(f"Transcribing file: {transcription.filename}")
        result = transcribe_audio(
            str(transcription.filename),
            model_size=model_size,
            language=language
        )

        # Update transcription with results
        transcription.text = result["text"]
        transcription.status = "completed"
        transcription.completed_at = datetime.utcnow()
        self.db.commit()

        logger.info(f"Transcription {transcription_id} completed successfully")
        return {
            "status": "completed",
            "transcription_id": transcription_id,
            "text": result["text"]
        }

    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        logger.error(error_msg)
        
        if transcription:
            transcription.status = "failed"
            transcription.error = error_msg
            self.db.commit()
        
        return {
            "status": "failed",
            "error": error_msg,
            "transcription_id": transcription_id
        }

@celery.task
def cleanup_old_files():
    """Periodic task to clean up old files and records"""
    logger.info("Starting cleanup task")
    db = SessionLocal()
    try:
        # Find old transcriptions (e.g., older than 30 days)
        cutoff = datetime.utcnow() - timedelta(days=30)
        old_transcriptions = db.query(Transcription).filter(
            Transcription.created_at < cutoff
        ).all()

        for trans in old_transcriptions:
            try:
                # Delete the file
                file_path = Path(trans.filename)
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted file: {trans.filename}")
                
                # Delete the database record
                db.delete(trans)
                logger.info(f"Deleted record for transcription {trans.id}")
                
            except Exception as e:
                logger.error(f"Error cleaning up transcription {trans.id}: {str(e)}")

        db.commit()
        logger.info("Cleanup task completed")
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise
    
    finally:
        db.close()

# Optional: Task for real-time progress updates
@celery.task(bind=True)
def update_progress(self, transcription_id: int, progress: float):
    """Update transcription progress"""
    try:
        db = SessionLocal()
        transcription = db.query(Transcription).filter(
            Transcription.id == transcription_id
        ).first()
        
        if transcription:
            # You could store progress in a Redis cache or WebSocket
            logger.info(f"Transcription {transcription_id} progress: {progress}%")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Failed to update progress: {str(e)}")