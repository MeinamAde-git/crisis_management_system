import os

class Settings:
    PROJECT_NAME: str = "Crisis & Social Threat Management System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./crisis.db"
    VIOLENCE_THRESHOLD: float = 0.65  # Threat score cutoff to trigger emergency alerts

settings = Settings()
