from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    cohere_api_key: str

    # Database settings
    neon_db_url: str

    # Qdrant settings
    qdrant_api_key: str
    qdrant_cluster_url: str
    qdrant_port: int = 6333

    # Application settings
    debug: bool = False
    log_level: str = "INFO"

    # Rate limiting (if applicable)
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # in seconds

    # Better Auth settings
    better_auth_secret: str
    better_auth_url: str

    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow both cases


def get_settings():
    return Settings()