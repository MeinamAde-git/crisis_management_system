import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, Enum as SQLAlchemyEnum
from app.db.session import Base

# 1. Enums for Responders
class ResponderType(str, enum.Enum):
    POLICE = "Police"
    FIRE = "Fire"
    MEDICAL = "Medical"

class ResponderStatus(str, enum.Enum):
    AVAILABLE = "Available"
    DISPATCHED = "Dispatched"
    OFF_DUTY = "Off Duty"

# 2. Restored Incident Model
class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    incident_type = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    severity_score = Column(Float, default=0.0)
    latitude = Column(Float)
    longitude = Column(Float)

# 3. Responder Model
class Responder(Base):
    __tablename__ = "responders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    unit_type = Column(SQLAlchemyEnum(ResponderType))
    latitude = Column(Float)
    longitude = Column(Float)
    is_available = Column(Boolean, default=True)
    status = Column(SQLAlchemyEnum(ResponderStatus), default=ResponderStatus.AVAILABLE)