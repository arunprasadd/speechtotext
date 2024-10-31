# backend/app/database.py
from sqlalchemy import create_engine, exc, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from .config import settings
import logging
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Configure database engine with pool settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,                  # Maximum number of permanent connections
    max_overflow=10,              # Maximum number of additional connections
    pool_timeout=30,              # Timeout for getting connection from pool
    pool_recycle=1800,           # Recycle connections after 30 minutes
    pool_pre_ping=True,          # Enable connection health checks
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency for database sessions"""
    db = SessionLocal()
    try:
        # Test the connection with text() wrapper
        db.execute(text("SELECT 1"))
        yield db
    except exc.OperationalError as e:
        logger.error(f"Database connection error: {str(e)}")
        # Try to reconnect
        for attempt in range(3):
            try:
                db.close()
                db = SessionLocal()
                db.execute(text("SELECT 1"))
                yield db
                break
            except exc.OperationalError as retry_error:
                logger.error(f"Retry {attempt + 1} failed: {str(retry_error)}")
                time.sleep(1)  # Wait before retrying
        else:
            raise HTTPException(status_code=500, detail="Database connection failed")
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)}")
        raise
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database operations with retry logic"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except exc.OperationalError as e:
        logger.error(f"Database operation failed: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database operation: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def check_db_connection():
    """Check if database connection is working"""
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False