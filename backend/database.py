"""
Database models for AI Reader application
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    """User model for authentication and subscription management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    subscription_tier = Column(String(50), default="free", nullable=False)
    role = Column(String(50), default="user", nullable=False)
    school_email = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Usage tracking
    api_calls_today = Column(Integer, default=0, nullable=False)
    tts_minutes_today = Column(Float, default=0.0, nullable=False)
    image_generations_today = Column(Integer, default=0, nullable=False)
    last_usage_reset = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class BroadcastSession(Base):
    """Broadcast generation session tracking"""
    __tablename__ = "broadcast_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    script_content = Column(Text, nullable=False)
    audio_file_path = Column(String(500), nullable=True)
    duration_seconds = Column(Integer, default=600, nullable=False)  # 10 minutes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), default="generating", nullable=False)  # generating, completed, failed
    
    def __repr__(self):
        return f"<BroadcastSession(id={self.id}, title='{self.title}', user_id={self.user_id})>"


class APIUsageLog(Base):
    """API usage logging for analytics"""
    __tablename__ = "api_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    response_status = Column(Integer, nullable=False)
    processing_time_ms = Column(Float, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<APIUsageLog(id={self.id}, user_id={self.user_id}, endpoint='{self.endpoint}')>"


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_reader.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")