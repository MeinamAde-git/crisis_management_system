from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Incident, Responder
from app.services.threat_service import analyze_threat
from app.services.geo_service import haversine_distance

router = APIRouter()


# --- Connection Manager for WebSockets ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_incident(self, incident_data: dict):
        for connection in self.active_connections:
            await connection.send_json({"event": "NEW_INCIDENT", "data": incident_data})


manager = ConnectionManager()


# --- Pydantic Schemas ---
class OSINTScanRequest(BaseModel):
    content: Optional[str] = None
    text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = "OSINT Stream"


class IncidentCreate(BaseModel):
    title: str
    # Added a default value so the frontend doesn't crash the request when it omits this field
    description: str = "Emergency reported via manual dispatch"
    incident_type: str = "SECURITY"
    severity_score: float = 0.5
    latitude: float
    longitude: float
    radius_km: float = 1.0
    status: str = "Active"
    source: str = "Manual Entry"


# --- Endpoints ---

@router.get("/responders/")
def list_responders(db: Session = Depends(get_db)):
    return db.query(Responder).all()


@router.websocket("/ws/incidents")
async def websocket_incidents(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/osint/threat-scanner")
async def scan_osint_feed(payload: OSINTScanRequest, db: Session = Depends(get_db)):
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

        await manager.broadcast_incident({
            "id": incident.id,
            "title": incident.title,
            "severity": incident.incident_type,
            "latitude": incident.latitude,
            "longitude": incident.longitude
        })

    return {
        "analysis": analysis,
        "escalated_to_incident": analysis["is_threat"],
        "incident_id": incident_id
    }


@router.get("/incidents/")
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()


@router.post("/incidents/")
async def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
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

    await manager.broadcast_incident({
        "id": incident.id,
        "title": incident.title,
        "severity": incident.incident_type,
        "latitude": incident.latitude,
        "longitude": incident.longitude
    })

    return {"status": "success", "data": incident}


@router.get("/incidents/{incident_id}/nearest-responders")
def get_nearest_responders(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    responders = db.query(Responder).filter(Responder.is_available == True).all()
    ranked = []
    for r in responders:
        dist = haversine_distance(incident.latitude, incident.longitude, r.latitude, r.longitude)
        ranked.append({
            "id": r.id,
            "name": r.name,
            "unit_type": str(r.unit_type.value),
            "distance_km": round(dist, 2),
            "latitude": r.latitude,
            "longitude": r.longitude
        })
    ranked.sort(key=lambda x: x["distance_km"])

    return {
        "incident_id": incident.id,
        "location": {"lat": incident.latitude, "lon": incident.longitude},
        "dispatched_candidates": ranked
    }