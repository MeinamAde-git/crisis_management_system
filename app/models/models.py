import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, Enum as SQLAlchemyEnum
from app.db.session import Base

# 1. Restore the missing Enums
class ResponderType(str, enum.Enum):
    POLICE = "Police"
    FIRE = "Fire"
    MEDICAL = "Medical"

class ResponderStatus(str, enum.Enum):
    AVAILABLE = "Available"
    DISPATCHED = "Dispatched"
    OFF_DUTY = "Off Duty"

# 2. Define the database table using the restored Enums
class Responder(Base):
    __tablename__ = "responders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    unit_type = Column(SQLAlchemyEnum(ResponderType))
    latitude = Column(Float)
    longitude = Column(Float)
    is_available = Column(Boolean, default=True)
    status = Column(SQLAlchemyEnum(ResponderStatus), default=ResponderStatus.AVAILABLE)