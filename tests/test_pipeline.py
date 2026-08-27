import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
from app.services.geo_service import haversine_distance
from app.services.threat_service import analyze_social_post

client = TestClient(app)

# 1. Unit Tests: Geospatial Calculations
def test_haversine_distance():
    dist = haversine_distance(12.9716, 77.5946, 12.9720, 77.5950)
    assert isinstance(dist, float)
    assert 0.0 < dist < 1.0

def test_haversine_zero_distance():
    dist = haversine_distance(12.9716, 77.5946, 12.9716, 77.5946)
    assert dist == 0.0

# 2. Unit Tests: Threat Analysis Engine
def test_threat_scanner_high_risk():
    text = "Violent mob with guns and rioting near City Center!"
    result = analyze_social_post(text)
    assert result["is_threat"] is True
    assert result["threat_score"] >= 0.70

def test_threat_scanner_benign_text():
    text = "Beautiful sunny morning having tea at the park."
    result = analyze_social_post(text)
    assert result["is_threat"] is False
    assert result["threat_score"] == 0.0

# 3. Integration Tests: Endpoints
def test_health_check_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_threat_scanner_api():
    payload = {
        "platform": "X/Twitter",
        "content": "Emergency! Bomb explosion and arson near North Market!"
    }
    response = client.post("/api/v1/osint/threat-scanner", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["escalated_to_incident"] is True
