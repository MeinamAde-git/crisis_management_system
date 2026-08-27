import re

# Comprehensive threat and violence signal keywords
VIOLENT_KEYWORDS = {
    "weapons": ["gun", "pistol", "rifle", "weapon", "knife", "machete", "explosive", "bomb", "ammunition", "shooting"],
    "riots_unrest": ["riot", "rioting", "mob", "clash", "tear gas", "vandalism", "arson", "burning", "looting", "barricade"],
    "assault_threat": ["attack", "attacking", "lynching", "assault", "ambush", "kill", "stabbing", "hostage", "threaten"]
}

LOCATION_DATABASE = {
    "central square": (12.9716, 77.5946),
    "city center": (12.9750, 77.6000),
    "main station": (12.9780, 77.5700),
    "metro station": (12.9800, 77.5800),
    "north market": (12.9900, 77.6100),
    "south gate": (12.9300, 77.6200),
    "downtown": (12.9650, 77.5900)
}

def analyze_social_post(text: str) -> dict:
    """Evaluates raw text for physical violence and unrest threats."""
    text_lower = text.lower()
    matched_flags = []
    
    # 1. Keyword Flagging
    for category, keywords in VIOLENT_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                matched_flags.append(f"{category}:{kw}")
                
    # 2. Threat Score Calculation
    base_score = min(1.0, len(matched_flags) * 0.28)
    if "bomb" in text_lower or "shooting" in text_lower or "gun" in text_lower:
        base_score = max(base_score, 0.85)
    threat_score = round(base_score, 2)
    
    # 3. Categorization
    if threat_score >= 0.70:
        threat_category = "High-Risk Violence Threat"
    elif threat_score >= 0.40:
        threat_category = "Civil Unrest Alert"
    else:
        threat_category = "Low / Informational"
        
    # 4. Location Entity Resolution
    detected_loc = "Unknown"
    coords = (12.9716, 77.5946) # Default city coordinates
    for loc_name, loc_coords in LOCATION_DATABASE.items():
        if loc_name in text_lower:
            detected_loc = loc_name.title()
            coords = loc_coords
            break
            
    return {
        "threat_score": threat_score,
        "threat_category": threat_category,
        "matched_flags": matched_flags,
        "is_threat": threat_score >= 0.65,
        "location_name": detected_loc,
        "latitude": coords[0],
        "longitude": coords[1]
    }
