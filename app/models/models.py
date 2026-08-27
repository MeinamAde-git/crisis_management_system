from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from app.db.session import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    incident_type = Column(String(100), nullable=False)  # e.g., "Fire", "Riot", "Flood", "Medical"
    severity = Column(String(50), default="Medium")      # "Low", "Medium", "High", "Critical"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, default=1.0)
    status = Column(String(50), default="Active")        # "Active", "Contained", "Resolved"
    source = Column(String(100), default="Manual SOS")   # "Manual SOS", "Social Media OSINT"
    created_at = Column(DateTime, default=datetime.utcnow)

class Responder(Base):
    __tablename__ = "responders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    unit_type = Column(String(100), nullable=False)      # "Ambulance", "Police", "Fire Squad"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    contact = Column(String(50), nullable=True)

class ThreatPost(Base):
    __tablename__ = "threat_posts"

    id = Column(Integer, primary_key=True, index=True)
    source_platform = Column(String(50))                 # "X/Twitter", "Telegram", "Reddit"
    raw_content = Column(Text, nullable=False)
    threat_score = Column(Float, nullable=False)         # 0.0 to 1.0
    threat_category = Column(String(100))                # "Violence", "Civil Unrest", "Safe"
    detected_location = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    escalated_to_incident = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
