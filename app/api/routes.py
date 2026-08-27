@router.post("/osint/threat-scanner")
def scan_osint_feed(payload: OSINTScanRequest, db: Session = Depends(get_db)):
    analysis = analyze_threat(
        text=payload.content,
        lat=payload.latitude,
        lon=payload.longitude
    )

    incident_id = None
    if analysis["is_threat"]:
        # Auto-escalate to live incident
        incident = Incident(
            title=f"OSINT: {analysis['threat_category']}",
            description=payload.content,
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