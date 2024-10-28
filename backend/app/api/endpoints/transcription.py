# backend/app/api/endpoints/transcription.py
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
from datetime import datetime
import logging
from typing import List
from app.models import Transcription
from app.database import get_db
from app.utils.transcription import transcribe_audio
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    language: str = "en",
    model_size: str = "base",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Upload and transcribe file"""
    # Validate file type
    if not file.filename.endswith(tuple(settings.ALLOWED_EXTENSIONS)):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    try:
        # Create uploads directory if it doesn't exist
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = settings.UPLOAD_DIR / safe_filename
        
        # Save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create transcription record
        transcription = Transcription(
            filename=str(file_path),
            original_filename=file.filename,
            file_size=file.size,
            status="pending",
            model_size=model_size,
            language=language
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)
        
        # Start transcription in background
        background_tasks.add_task(
            process_transcription,
            transcription.id,
            db
        )
        
        return JSONResponse(
            content={
                "id": transcription.id,
                "status": "pending",
                "message": "File uploaded successfully"
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{transcription_id}")
async def get_transcription_status(
    transcription_id: int,
    db: Session = Depends(get_db)
):
    """Get transcription status and result"""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()
    
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return {
        "id": transcription.id,
        "status": transcription.status,
        "text": transcription.text if transcription.status == "completed" else None,
        "error": transcription.error if transcription.status == "failed" else None
    }

@router.get("/")
async def list_transcriptions(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all transcriptions"""
    transcriptions = db.query(Transcription)\
        .order_by(Transcription.created_at.desc())\
        .offset(skip).limit(limit).all()
    return transcriptions

def process_transcription(transcription_id: int, db: Session):
    """Background task to process transcription"""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()
    
    if not transcription:
        logger.error(f"Transcription {transcription_id} not found")
        return
    
    try:
        # Update status to processing
        transcription.status = "processing"
        db.commit()
        
        # Perform transcription
        result = transcribe_audio(
            str(transcription.filename),
            language=transcription.language,
            model_size=transcription.model_size
        )
        
        # Update transcription with results
        transcription.text = result["text"]
        transcription.status = "completed"
        transcription.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Transcription {transcription_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        transcription.status = "failed"
        transcription.error = str(e)
        db.commit()