import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS coordinates in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)

def find_nearest_responders(incident_lat: float, incident_lon: float, responders: list, max_distance_km: float = 25.0):
    """Sort and filter responders by proximity to the incident."""
    results = []
    for r in responders:
        dist = haversine_distance(incident_lat, incident_lon, r.latitude, r.longitude)
        if dist <= max_distance_km:
            results.append({
                "responder_id": r.id,
                "name": r.name,
                "unit_type": r.unit_type,
                "distance_km": dist,
                "is_available": r.is_available,
                "contact": r.contact
            })
    return sorted(results, key=lambda x: x["distance_km"])
