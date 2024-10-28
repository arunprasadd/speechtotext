# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from datetime import datetime
from .database import Base

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    original_filename = Column(String)
    file_size = Column(Integer)
    duration = Column(Float, nullable=True)
    status = Column(String)  # pending, processing, completed, failed
    model_size = Column(String)
    language = Column(String)
    text = Column(Text, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)