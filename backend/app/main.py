from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import transcription
from .config import settings
from .database import engine
from . import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Speech to Text API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(
    transcription.router,
    prefix="/transcription",
    tags=["transcription"]
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}