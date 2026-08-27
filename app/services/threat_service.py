from typing import Dict, Any, List

CRITICAL_KEYWORDS = {
    "explosion": 0.95,
    "bomb": 0.95,
    "terrorist": 0.90,
    "shooter": 0.90,
    "gunfire": 0.85,
    "fire": 0.80,
    "blast": 0.85,
    "chemical": 0.80,
    "casualties": 0.85,
    "collapse": 0.75,
    "flood": 0.70,
    "earthquake": 0.80,
    "hostage": 0.90,
    "emergency": 0.65
}


def analyze_threat(text: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
    text_lower = (text or "").lower()
    matched_flags: List[str] = []
    max_score = 0.0

    for word, weight in CRITICAL_KEYWORDS.items():
        if word in text_lower:
            matched_flags.append(word)
            if weight > max_score:
                max_score = weight

    if len(matched_flags) > 1:
        max_score = min(1.0, max_score + 0.05 * (len(matched_flags) - 1))

    is_threat = max_score >= 0.60

    if max_score >= 0.80:
        category = "Critical / Imminent Threat"
    elif max_score >= 0.60:
        category = "High Alert"
    elif max_score >= 0.40:
        category = "Medium Caution"
    else:
        category = "Low / Informational"

    return {
        "threat_score": round(max_score, 2),
        "threat_category": category,
        "matched_flags": matched_flags,
        "is_threat": is_threat,
        "location_name": "Reported Area",
        "latitude": lat if lat is not None else 28.6139,
        "longitude": lon if lon is not None else 77.2090
    }