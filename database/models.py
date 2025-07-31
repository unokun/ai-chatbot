from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class CorrectionHistory(Base):
    __tablename__ = "correction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    correction_type = Column(String, nullable=False)
    ai_model_used = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    user_id = Column(String, primary_key=True, index=True)
    preferred_ai_model = Column(String, default="openai-gpt4o")
    default_correction_style = Column(String, default="polite")

DATABASE_URL = "sqlite:///./correction_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()