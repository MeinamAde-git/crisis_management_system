import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.routes import router
from app.db.session import engine, Base

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Emergency Response, Geospatial Intelligence & Dynamic Dispatch",
    version="1.0.0"
)

# Include API Router
app.include_router(router, prefix=settings.API_V1_STR)

# Find static directory
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"
INDEX_FILE = STATIC_DIR / "index.html"

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard():
    # Read HTML file if present
    if INDEX_FILE.is_file():
        return HTMLResponse(content=INDEX_FILE.read_text(encoding="utf-8"))

    # Inline Dashboard Fallback
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AEGIS Crisis Command Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    </head>
    <body class="bg-slate-900 text-slate-100 h-screen flex flex-col font-sans">
        <header class="bg-slate-800/80 backdrop-blur border-b border-slate-700 px-6 py-4 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <span class="text-2xl font-black bg-gradient-to-r from-red-500 to-amber-500 bg-clip-text text-transparent">AEGIS CORE</span>
                <span class="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-mono">LIVE CLOUD</span>
            </div>
            <a href="/docs" target="_blank" class="text-xs text-sky-400 hover:underline">Interactive API Docs &rarr;</a>
        </header>
        <div class="flex-1 flex">
            <div id="map" class="flex-1 h-full z-0 bg-slate-950"></div>
            <div class="w-96 bg-slate-800/90 border-l border-slate-700 p-4 flex flex-col space-y-4">
                <h3 class="text-sm font-bold tracking-wider text-slate-400 uppercase">Live Crisis Dispatch</h3>
                <div id="feed" class="flex-1 overflow-y-auto space-y-2 text-xs font-mono text-slate-300">
                    <div class="p-2.5 rounded bg-slate-900/80 border border-slate-700">Connecting to telemetry network...</div>
                </div>
            </div>
        </div>
        <script>
            const map = L.map('map').setView([28.6139, 77.2090], 12);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap &copy; CARTO'
            }).addTo(map);

            async function loadIncidents() {
                try {
                    const res = await fetch('/api/v1/incidents/');
                    const incidents = await res.json();
                    const feed = document.getElementById('feed');
                    feed.innerHTML = '';
                    incidents.forEach(inc => {
                        L.circleMarker([inc.latitude, inc.longitude], {
                            radius: 8,
                            color: inc.severity_score >= 0.7 ? '#ef4444' : '#f59e0b',
                            fillOpacity: 0.8
                        }).addTo(map).bindPopup(`<b>${inc.title}</b><br>Score: ${inc.severity_score}`);
                        feed.innerHTML += `<div class="p-2.5 rounded bg-slate-900/80 border border-slate-700"><p class="font-bold text-red-400">${inc.title}</p><p class="text-slate-400">${inc.description}</p></div>`;
                    });
                } catch(e) { console.error(e); }
            }
            loadIncidents();
        </script>
    </body>
    </html>
    """)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)