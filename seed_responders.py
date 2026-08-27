import httpx

API_BASE = "http://127.0.0.1:8000/api/v1/responders/"

UNITS = [
    {"name": "Alpha-1 Rapid Police Unit", "unit_type": "Police", "latitude": 12.9730, "longitude": 77.5960, "contact": "+91-9876500001"},
    {"name": "Bravo-2 SWAT & Anti-Riot", "unit_type": "Police", "latitude": 12.9760, "longitude": 77.5850, "contact": "+91-9876500002"},
    {"name": "City Med Care Ambulance 01", "unit_type": "Ambulance", "latitude": 12.9700, "longitude": 77.6010, "contact": "+91-9876500003"},
    {"name": "Trauma Life Medic 09", "unit_type": "Ambulance", "latitude": 12.9820, "longitude": 77.5750, "contact": "+91-9876500004"},
    {"name": "Station 4 Fire Squad Alpha", "unit_type": "Fire Squad", "latitude": 12.9890, "longitude": 77.6050, "contact": "+91-9876500005"},
    {"name": "South Sector Fire Brigade", "unit_type": "Fire Squad", "latitude": 12.9350, "longitude": 77.6180, "contact": "+91-9876500006"}
]

with httpx.Client() as client:
    for unit in UNITS:
        r = client.post(API_BASE, json=unit)
        print(f"Registered {unit['name']}: {r.status_code}")
