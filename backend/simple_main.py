"""
Simplified Employee Monitoring System without DeepFace
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import random

load_dotenv()

# Database Setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./employee_monitoring.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class DetectionLog(Base):
    __tablename__ = "detection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, default="EMP001")
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_present = Column(Integer)
    emotion = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)

Base.metadata.create_all(bind=engine)

# Pydantic Models
class DetectionResponse(BaseModel):
    id: int
    employee_id: str
    timestamp: datetime
    is_present: bool
    emotion: Optional[str]
    confidence: Optional[float]

class AnalyticsResponse(BaseModel):
    total_detections: int
    presence_percentage: float
    emotion_distribution: dict
    working_hours: float

app = FastAPI(title="Employee Monitoring System (Simple)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock emotion detector
class MockEmotionDetector:
    def __init__(self):
        self.emotions = ['happy', 'neutral', 'sad', 'surprise']
    
    def get_detection(self):
        is_present = random.random() > 0.3  # 70% chance of presence
        emotion = random.choice(self.emotions) if is_present else None
        confidence = round(random.uniform(70, 95), 1) if is_present else None
        
        return is_present, emotion, confidence

detector = MockEmotionDetector()

@app.get("/")
async def root():
    return {
        "message": "Employee Monitoring System (Simple Mode)",
        "status": "running",
        "note": "Using mock data - computer vision libraries not available"
    }

@app.post("/api/detection", response_model=DetectionResponse)
async def create_detection(employee_id: str = "EMP001"):
    db = SessionLocal()
    try:
        is_present, emotion, confidence = detector.get_detection()
        
        detection = DetectionLog(
            employee_id=employee_id,
            is_present=1 if is_present else 0,
            emotion=emotion,
            confidence=confidence
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)
        
        return {
            "id": detection.id,
            "employee_id": detection.employee_id,
            "timestamp": detection.timestamp,
            "is_present": bool(detection.is_present),
            "emotion": detection.emotion,
            "confidence": detection.confidence
        }
    finally:
        db.close()

@app.get("/api/detections", response_model=List[DetectionResponse])
async def get_detections(
    employee_id: str = "EMP001",
    limit: int = 100
):
    db = SessionLocal()
    try:
        detections = db.query(DetectionLog).filter(
            DetectionLog.employee_id == employee_id
        ).order_by(DetectionLog.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "id": d.id,
                "employee_id": d.employee_id,
                "timestamp": d.timestamp,
                "is_present": bool(d.is_present),
                "emotion": d.emotion,
                "confidence": d.confidence
            }
            for d in detections
        ]
    finally:
        db.close()

@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics(employee_id: str = "EMP001", days: int = 1):
    db = SessionLocal()
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        detections = db.query(DetectionLog).filter(
            DetectionLog.employee_id == employee_id,
            DetectionLog.timestamp >= start_date
        ).all()
        
        if not detections:
            return {
                "total_detections": 0,
                "presence_percentage": 0.0,
                "emotion_distribution": {},
                "working_hours": 0.0
            }
        
        total = len(detections)
        present_count = sum(1 for d in detections if d.is_present)
        presence_percentage = (present_count / total * 100) if total > 0 else 0
        
        emotion_counts = {}
        for d in detections:
            if d.emotion and d.is_present:
                emotion_counts[d.emotion] = emotion_counts.get(d.emotion, 0) + 1
        
        working_hours = (present_count * 0.5) / 60
        
        return {
            "total_detections": total,
            "presence_percentage": round(presence_percentage, 2),
            "emotion_distribution": emotion_counts,
            "working_hours": round(working_hours, 2)
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)