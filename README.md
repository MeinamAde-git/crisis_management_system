# AEGIS: Real-Time AI Social Threat Intelligence & Geospatial Crisis Dispatch

AEGIS is an event-driven crisis management and early-warning intelligence platform. It automates the ingestion of unstructured social media and citizen distress feeds, analyzes threat severity via natural language processing, dynamically maps crisis epicenters, and computes optimal responder dispatch vectors in sub-second latency.

---

## Key Features

* **Automated OSINT Threat Ingestion:** Ingests live text streams (X/Twitter, Telegram, Reddit) and evaluates threat severity scores and entity coordinates.
* **Geospatial Proximity Routing:** Computes great-circle distances using the Haversine formula to rank and dispatch nearest available emergency units (Police, SWAT, Paramedics, Fire Brigades).
* **Live WebSocket Telemetry:** Broadcasts newly escalated threats and emergency calls to all active dispatch operator consoles without polling.
* **Interactive Command Center:** Interactive web dashboard built with Leaflet.js and TailwindCSS featuring real-time map clustering, dynamic routing vectors, and distress reporting.
* **Automated Test Coverage:** Complete Pytest integration and unit test suite verifying geospatial calculations, threat classification, and RESTful lifecycle operations.

---

## System Architecture

[ Citizen Reports / SOS Form ]
                                            │
[ Public OSINT Stream ]                         │ (HTTP POST)
(Twitter, Telegram)                           ▼
│                     ┌──────────────────────────────┐
▼ (HTTP POST)         │    FastAPI Application Core   │
┌──────────────────────┐         │   - Pydantic Validation      │
│ Threat Scoring Engine│ ──────> │   - SQLAlchemy ORM           │
│ (NLP Entity & Score) │         │   - WebSocket Manager        │
└──────────────────────┘         └──────────────┬───────────────┘
│
┌──────────────────────────────┴──────────────────────────────┐
▼                                                             ▼
┌──────────────────────────────┐                              ┌──────────────────────────────┐
│  Geospatial Dispatch Engine  │                              │   Real-Time Event Broadcast  │
│  - Haversine Proximity       │                              │   - WebSocket Telemetry Push │
│  - Route Vector Generation   │                              └──────────────┬───────────────┘
└──────────────┬───────────────┘                                             │
│                                                             ▼
▼                                              ┌──────────────────────────────┐
┌──────────────────────────────┐                              │ Command Center Web Dashboard │
│ SQLite / PostgreSQL Storage  │                              │ (Leaflet Map + Live Routing) │
└──────────────────────────────┘                              └──────────────────────────────┘


---

## Tech Stack

* **Backend:** Python 3.11+, FastAPI, Starlette, Pydantic v2, Uvicorn
* **Database & ORM:** SQLite / PostgreSQL, SQLAlchemy
* **Geospatial & Real-time:** Haversine Proximity Math, Native WebSockets
* **Frontend:** Vanilla JavaScript (ES6+), Leaflet.js, TailwindCSS
* **Testing & Simulation:** PyTest, PyTest-Asyncio, HTTPX

---

## API Reference

### OSINT Ingestion & Incidents
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/osint/threat-scanner` | Ingest and score raw text; auto-escalates critical threats. |
| `GET` | `/api/v1/incidents/` | Retrieve all active crisis incidents. |
| `POST` | `/api/v1/incidents/` | Create a manual citizen emergency record. |
| `GET` | `/api/v1/incidents/{id}/nearest-responders` | Compute proximity-ranked responder units for an incident. |

### Responders & WebSockets
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/responders/` | List all registered emergency units. |
| `POST` | `/api/v1/responders/` | Register a new response unit with GPS coordinates. |
| `WS` | `/api/v1/ws/incidents` | Live WebSocket endpoint streaming real-time alerts. |

---

## Quickstart Setup

### 1. Clone & Setup Environment
```bash
git clone [https://github.com/yourusername/crisis_management_system.git](https://github.com/yourusername/crisis_management_system.git)
cd crisis_management_system
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


