from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import json

from app.db.session import get_db
from app.models.models import Incident, Responder, ThreatPost
from app.services.geo_service import find_nearest_responders
from app.services.threat_service import analyze_social_post

router = APIRouter()

# --- Active WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/incidents")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Pydantic Schemas ---
class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    incident_type: str
    severity: str = "Medium"
    latitude: float
    longitude: float
    radius_km: float = 1.0

class SocialPostIngest(BaseModel):
    platform: str = "X/Twitter"
    content: str

class ResponderCreate(BaseModel):
    name: str
    unit_type: str
    latitude: float
    longitude: float
    contact: Optional[str] = None

# --- Routes ---
@router.post("/incidents/")
async def report_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(**incident.model_dump())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    # Broadcast to all connected clients in real time
    await manager.broadcast({
        "event": "NEW_INCIDENT",
        "data": {
            "id": db_incident.id,
            "title": db_incident.title,
            "description": db_incident.description,
            "incident_type": db_incident.incident_type,
            "severity": db_incident.severity,
            "latitude": db_incident.latitude,
            "longitude": db_incident.longitude
        }
    })
    return {"status": "success", "data": db_incident}

@router.get("/incidents/")
def list_active_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).filter(Incident.status == "Active").all()

@router.get("/responders/")
def list_responders(db: Session = Depends(get_db)):
    return db.query(Responder).all()

@router.post("/responders/")
def register_responder(resp: ResponderCreate, db: Session = Depends(get_db)):
    db_resp = Responder(**resp.model_dump())
    db.add(db_resp)
    db.commit()
    db.refresh(db_resp)
    return {"status": "success", "data": db_resp}

@router.get("/incidents/{incident_id}/nearest-responders")
def get_nearest_responders(incident_id: int, max_distance_km: float = 20.0, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    responders = db.query(Responder).filter(Responder.is_available == True).all()
    nearest = find_nearest_responders(incident.latitude, incident.longitude, responders, max_distance_km)
    
    # Enrich with responder coordinates for map polyline routing
    for candidate in nearest:
        resp_obj = next((r for r in responders if r.id == candidate["responder_id"]), None)
        if resp_obj:
            candidate["latitude"] = resp_obj.latitude
            candidate["longitude"] = resp_obj.longitude

    return {
        "incident_id": incident.id,
        "incident_title": incident.title,
        "location": {"lat": incident.latitude, "lon": incident.longitude},
        "dispatched_candidates": nearest
    }

@router.post("/osint/threat-scanner")
async def scan_and_escalate_social_post(post_data: SocialPostIngest, db: Session = Depends(get_db)):
    analysis = analyze_social_post(post_data.content)
    
    threat_record = ThreatPost(
        source_platform=post_data.platform,
        raw_content=post_data.content,
        threat_score=analysis["threat_score"],
        threat_category=analysis["threat_category"],
        detected_location=analysis["location_name"],
        latitude=analysis["latitude"],
        longitude=analysis["longitude"],
        escalated_to_incident=analysis["is_threat"]
    )
    db.add(threat_record)
    
    escalated_incident_id = None
    if analysis["is_threat"]:
        auto_incident = Incident(
            title=f"🚨 AI Alert: {analysis['threat_category']} at {analysis['location_name']}",
            description=f"Auto-escalated from {post_data.platform}: '{post_data.content}'",
            incident_type="Civil Violence & Unrest",
            severity="Critical" if analysis["threat_score"] >= 0.85 else "High",
            latitude=analysis["latitude"],
            longitude=analysis["longitude"],
            radius_km=2.0,
            source=f"OSINT-{post_data.platform}"
        )
        db.add(auto_incident)
        db.commit()
        db.refresh(auto_incident)
        escalated_incident_id = auto_incident.id

        await manager.broadcast({
            "event": "NEW_INCIDENT",
            "data": {
                "id": auto_incident.id,
                "title": auto_incident.title,
                "description": auto_incident.description,
                "incident_type": auto_incident.incident_type,
                "severity": auto_incident.severity,
                "latitude": auto_incident.latitude,
                "longitude": auto_incident.longitude
            }
        })
    else:
        db.commit()
        
    return {
        "analysis": analysis,
        "escalated_to_incident": analysis["is_threat"],
        "incident_id": escalated_incident_id
    }
