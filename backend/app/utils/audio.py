# backend/app/utils/audio.py
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
import uuid
from ..config import settings
import logging

logger = logging.getLogger(__name__)

def record_audio(duration: int) -> Path:
    """Record audio using microphone"""
    try:
        recording = sd.rec(
            int(duration * settings.SAMPLE_RATE),
            samplerate=settings.SAMPLE_RATE,
            channels=1
        )
        sd.wait()
        
        filename = f"recording_{uuid.uuid4()}.wav"
        file_path = settings.RECORDINGS_DIR / filename
        
        sf.write(str(file_path), recording, settings.SAMPLE_RATE)
        return file_path
    except Exception as e:
        logger.error(f"Recording failed: {str(e)}")
        raise

# backend/app/utils/transcription.py
import whisper
from pathlib import Path
from typing import Dict, Any
import logging
from ..config import settings

logger = logging.getLogger(__name__)

def transcribe_audio(
    file_path: str,
    model_size: str = "base",
    language: str = "en"
) -> Dict[str, Any]:
    """Transcribe audio file using Whisper"""
    try:
        logger.info(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        logger.info(f"Starting transcription: {file_path}")
        result = model.transcribe(
            file_path,
            language=language,
            task="transcribe",
            temperature=0.0,
            compression_ratio_threshold=2.4,
            no_speech_threshold=0.6,
            condition_on_previous_text=True,
            fp16=False
        )
        
        return {
            "text": result["text"],
            "language": result.get("language", language),
            "segments": result.get("segments", [])
        }
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise