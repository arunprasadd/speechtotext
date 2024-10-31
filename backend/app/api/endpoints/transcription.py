# backend/app/api/endpoints/transcription.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import shutil
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Tuple, Optional
import os
from tenacity import retry, stop_after_attempt, wait_exponential
from app.models import Transcription
from app.database import get_db
from app.celery.tasks import transcribe_audio_task
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

async def validate_file_size(file: UploadFile) -> int:
    """Validate file size with proper error handling"""
    try:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        
        max_size = settings.MAX_FILE_SIZE
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({file_size / (1024*1024):.2f}MB) exceeds maximum allowed size ({max_size / (1024*1024):.2f}MB)"
            )
        return file_size
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating file size: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error validating file size"
        )
@router.get("/{transcription_id}")
async def get_transcription_status(transcription_id: int, db: Session = Depends(get_db)):
    """Get transcription status and result"""
    logger.info(f"Getting status for transcription ID: {transcription_id}")
    
    try:
        transcription = db.query(Transcription).filter(
            Transcription.id == transcription_id
        ).first()
        
        if not transcription:
            logger.error(f"Transcription {transcription_id} not found in database")
            raise HTTPException(status_code=404, detail="Transcription not found")
        
        logger.info(f"Found transcription with status: {transcription.status}")
        
        return {
            "id": transcription.id,
            "status": transcription.status,
            "text": transcription.text if transcription.status == "completed" else None,
            "error": transcription.error if transcription.status == "failed" else None,
            "file_size": transcription.file_size,
            "original_filename": transcription.original_filename,
            "created_at": transcription.created_at,
            "completed_at": transcription.completed_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcription status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking status: {str(e)}")
    
def create_transcription_record(
    db: Session,
    file_path: str,
    filename: str,
    file_size: int,
    model_size: str,
    language: str
) -> Transcription:
    """Create transcription record with retry logic"""
    try:
        transcription = Transcription(
            filename=str(file_path),
            original_filename=filename,
            file_size=file_size,
            status="pending",
            model_size=model_size,
            language=language,
            created_at=datetime.utcnow()
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)
        return transcription
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during transcription creation: {str(e)}")
        raise

def get_estimated_time(file_size: int, model_size: str) -> str:
    """Calculate estimated processing time based on file size and model"""
    # Basic estimation logic - can be refined based on actual performance data
    base_time = file_size / (1024 * 1024 * 5)  # 5MB per minute as base rate
    model_multipliers = {
        "tiny": 0.5,
        "base": 1,
        "small": 1.5,
        "medium": 2,
        "large": 3
    }
    estimated_minutes = base_time * model_multipliers.get(model_size, 1)
    
    if estimated_minutes < 1:
        return "less than a minute"
    elif estimated_minutes < 5:
        return "about 5 minutes"
    else:
        return f"about {int(estimated_minutes)} minutes"
@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(
    file: UploadFile = File(...),
    language: str = "en",
    model_size: str = "base",
    db: Session = Depends(get_db)
):
    """Upload and transcribe file"""
    logger.info(f"Received upload request for file: {file.filename}")
    file_path = None
    
    try:
        # Validate model size
        logger.info(f"Validating model size: {model_size}")
        if model_size not in settings.WHISPER_MODELS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model size. Allowed models: {list(settings.WHISPER_MODELS.keys())}"
            )
        
        # Validate language
        logger.info(f"Validating language: {language}")
        if language not in settings.SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language. Supported languages: {list(settings.SUPPORTED_LANGUAGES.keys())}"
            )
        
        # Validate file size
        logger.info("Validating file size")
        file_size = await validate_file_size(file)
        logger.info(f"File size validated: {file_size} bytes")
        
        # Validate file type
        logger.info("Validating file type")
        if not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Upload directory created/verified: {upload_dir}")

        # Changed this part to use the correct async function
        try:
            # Save file using the async function defined above
            file_path = await save_file(file, upload_dir)
            logger.info(f"File saved successfully at: {file_path}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )

        try:
            # Create transcription record
            transcription = create_transcription_record(
                db=db,
                file_path=str(file_path),
                filename=file.filename,
                file_size=file_size,
                model_size=model_size,
                language=language
            )
            
            # Start Celery task
            task = transcribe_audio_task.delay(transcription.id)
            
            estimated_time = get_estimated_time(file_size, model_size)
            
            return JSONResponse(
                content={
                    "id": transcription.id,
                    "status": "pending",
                    "message": "File uploaded successfully. Transcription started.",
                    "file_size": file_size,
                    "estimated_time": estimated_time,
                    "task_id": task.id,
                    "model": model_size,
                    "language": language
                },
                status_code=status.HTTP_202_ACCEPTED
            )
            
        except Exception as e:
            logger.error(f"Error in database operation: {str(e)}")
            # Clean up file if database operation fails
            if file_path and Path(file_path).exists():
                try:
                    Path(file_path).unlink()
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up file: {str(cleanup_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        if file_path and Path(file_path).exists():
            try:
                Path(file_path).unlink()
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up file: {str(cleanup_error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error - Please try again later"
        )