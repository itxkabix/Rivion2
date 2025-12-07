from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json
import logging
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Models
class SessionUser(Base):
    __tablename__ = 'session_user'
    session_id = Column(String, primary_key=True)
    user_name = Column(String)
    captured_image_base64 = Column(String)
    captured_image_path = Column(String)
    embedding = Column(LargeBinary)  # Changed from BYTEA to LargeBinary
    status = Column(String, default='searching')
    privacy_policy_agreed = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class EmotionLog(Base):
    __tablename__ = 'emotion_log'
    emotion_id = Column(String, primary_key=True)
    image_id = Column(String)
    session_id = Column(String)
    emotion_label = Column(String)
    confidence = Column(Float)
    emotion_distribution = Column(JSON)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

class SessionAggregatedEmotion(Base):
    __tablename__ = 'session_aggregated_emotion'
    aggregation_id = Column(String, primary_key=True)
    session_id = Column(String, unique=True)
    dominant_emotion = Column(String)
    emotion_confidence = Column(Float)
    emotion_distribution = Column(JSON)
    statement = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)

# Database operations
def insert_session_user(session_id: str, user_name: str, captured_image_base64: str, privacy_policy_agreed: bool):
    """Insert session user"""
    try:
        session = SessionLocal()
        expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRY_HOURS)
        user = SessionUser(
            session_id=session_id,
            user_name=user_name,
            captured_image_base64=captured_image_base64,
            privacy_policy_agreed=str(privacy_policy_agreed),
            expires_at=expires_at,
            status='searching'
        )
        session.add(user)
        session.commit()
        session.close()
        logger.info(f"Session user inserted: {session_id}")
    except Exception as e:
        logger.error(f"Error inserting session user: {e}")
        raise

def insert_emotion_log(image_id: str, session_id: str, emotion_label: str, confidence: float, emotion_distribution: dict):
    """Insert emotion log"""
    try:
        import uuid
        session = SessionLocal()
        log = EmotionLog(
            emotion_id=str(uuid.uuid4()),
            image_id=image_id,
            session_id=session_id,
            emotion_label=emotion_label,
            confidence=confidence,
            emotion_distribution=emotion_distribution,
        )
        session.add(log)
        session.commit()
        session.close()
        logger.info(f"Emotion log inserted: {emotion_label}")
    except Exception as e:
        logger.error(f"Error inserting emotion log: {e}")

def insert_aggregated_emotion(session_id: str, dominant_emotion: str, emotion_confidence: float, emotion_distribution: dict, statement: str):
    """Insert aggregated emotion"""
    try:
        import uuid
        session = SessionLocal()
        agg = SessionAggregatedEmotion(
            aggregation_id=str(uuid.uuid4()),
            session_id=session_id,
            dominant_emotion=dominant_emotion,
            emotion_confidence=emotion_confidence,
            emotion_distribution=emotion_distribution,
            statement=statement,
        )
        session.add(agg)
        session.commit()
        session.close()
        logger.info(f"Aggregated emotion inserted: {session_id}")
    except Exception as e:
        logger.error(f"Error inserting aggregated emotion: {e}")

def get_matched_images(embedding: np.ndarray, limit: int = 50, threshold: float = 0.6) -> list:
    """Get matched images from FAISS"""
    # Placeholder: In real implementation, query FAISS
    return [
        {
            'image_id': '1',
            'image_url': 'https://example.com/image1.jpg',
            'image_path': '/path/to/image1.jpg',
            'similarity_score': 0.95,
        },
        # ... more images
    ]

def delete_session(session_id: str):
    """Delete session and related data"""
    try:
        session = SessionLocal()
        session.query(SessionUser).filter(SessionUser.session_id == session_id).delete()
        session.query(EmotionLog).filter(EmotionLog.session_id == session_id).delete()
        session.query(SessionAggregatedEmotion).filter(SessionAggregatedEmotion.session_id == session_id).delete()
        session.commit()
        session.close()
        logger.info(f"Session deleted: {session_id}")
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
