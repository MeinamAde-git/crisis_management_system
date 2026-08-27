from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Incident, Responder
from app.services.threat_service import analyze_threat
from app.services.geo_service import calculate_haversine_distance

router = APIRouter()


# --- Pydantic Schemas ---
class OSINTScanRequest(BaseModel):
    content: Optional[str] = None
    text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = "OSINT Stream"


class IncidentCreate(BaseModel):
    title: str
    description: str
    incident_type: str = "SECURITY"
    severity_score: float = 0.5
    latitude: float
    longitude: float
    radius_km: float = 1.0
    status: str = "Active"
    source: str = "Manual Entry"


# --- Endpoints ---
@router.post("/osint/threat-scanner")
def scan_osint_feed(payload: OSINTScanRequest, db: Session = Depends(get_db)):
    raw_text = payload.content or payload.text or ""
    analysis = analyze_threat(
        text=raw_text,
        lat=payload.latitude,
        lon=payload.longitude
    )

    incident_id = None
    if analysis["is_threat"]:
        incident = Incident(
            title=f"OSINT: {analysis['threat_category']}",
            description=raw_text,
            incident_type="CRITICAL" if analysis["threat_score"] >= 0.8 else "SECURITY",
            severity_score=analysis["threat_score"],
            latitude=analysis["latitude"],
            longitude=analysis["longitude"],
            radius_km=2.0,
            status="Active",
            source=payload.source or "OSINT Stream"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        incident_id = incident.id

    return {
        "analysis": analysis,
        "escalated_to_incident": analysis["is_threat"],
        "incident_id": incident_id
    }


@router.get("/incidents/")
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()


@router.post("/incidents/")
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(
        title=payload.title,
        description=payload.description,
        incident_type=payload.incident_type,
        severity_score=payload.severity_score,
        latitude=payload.latitude,
        longitude=payload.longitude,
        radius_km=payload.radius_km,
        status=payload.status,
        source=payload.source
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return {"status": "success", "data": incident}


@router.get("/incidents/{incident_id}/nearest-responders")
def get_nearest_responders(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    responders = db.query(Responder).filter(Responder.is_available == True).all()
    ranked = []
    for r in responders:
        dist = calculate_haversine_distance(incident.latitude, incident.longitude, r.latitude, r.longitude)
        ranked.append({
            "id": r.id,
            "name": r.name,
            "unit_type": str(r.unit_type),
            "distance_km": round(dist, 2),
            "latitude": r.latitude,
            "longitude": r.longitude
        })
    ranked.sort(key=lambda x: x["distance_km"])
    return {"incident_id": incident.id, "nearest_responders": ranked}