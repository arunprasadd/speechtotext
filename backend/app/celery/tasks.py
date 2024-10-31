# backend/app/celery/tasks.py
from . import celery_app
from typing import Dict, Any
import whisper
import logging
from pathlib import Path
from datetime import datetime
from ..database import SessionLocal
from ..models import Transcription
from ..config import settings

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, 
            name='transcribe_audio_task',
            max_retries=3,
            soft_time_limit=3300,
            time_limit=3600)
def transcribe_audio_task(self, transcription_id: int):
    logger.info(f"Starting transcription task for ID: {transcription_id}")
    
    db = SessionLocal()
    try:
        # Log directory contents
        import os
        logger.info(f"Contents of uploads directory: {os.listdir('/app/uploads')}")
        
        transcription = db.query(Transcription).filter(
            Transcription.id == transcription_id
        ).first()
        
        if not transcription:
            logger.error(f"Transcription {transcription_id} not found in database")
            return
            
        logger.info(f"Processing file: {transcription.filename}")
        transcription.status = "processing"
        db.commit()

        # Check if file exists
        file_path = Path(transcription.filename)
        if not file_path.exists():
            logger.error(f"File not found at path: {file_path}")
            transcription.status = "failed"
            transcription.error = f"File not found at path: {file_path}"
            db.commit()
            return

        # Load model with logging
        logger.info(f"Loading Whisper model: {transcription.model_size}")
        model = whisper.load_model(transcription.model_size)
        
        # Transcribe
        logger.info("Starting transcription process")
        result = model.transcribe(str(file_path))
        
        logger.info("Transcription completed successfully")
        transcription.text = result["text"]
        transcription.status = "completed"
        transcription.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        logger.error(f"Error in transcription task: {str(e)}")
        transcription.status = "failed"
        transcription.error = str(e)
        db.commit()
        raise
    finally:
        db.close()