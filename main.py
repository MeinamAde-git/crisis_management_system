import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api.routes import router
from app.db.session import engine, Base

# Initialize database schemas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Emergency Response, Geospatial Intelligence & Dynamic Dispatch",
    version="1.0.0"
)

# Mount API endpoints
app.include_router(router, prefix=settings.API_V1_STR)

# Locate static folder safely using Pathlib
STATIC_DIR = Path(__file__).resolve().parent / "app" / "static"

# Direct root endpoint fallback
@app.get("/", include_in_schema=False)
async def read_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(str(index_file))
    return {"status": "online", "message": "AEGIS API is active. Go to /docs"}

# Mount static files directory
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)