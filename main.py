from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Emergency Response, Geospatial Dispatch, and OSINT Violence Threat Intelligence.",
    version="1.0.0"
)

# Mount API routes
app.include_router(router, prefix=settings.API_V1_STR)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def serve_dashboard():
    return FileResponse("app/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
