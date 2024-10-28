# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TranscriptionBase(BaseModel):
    original_filename: str
    language: str = "en"
    model_size: str = "base"

class TranscriptionCreate(TranscriptionBase):
    file_size: int

class Transcription(TranscriptionBase):
    id: int
    status: str
    text: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True