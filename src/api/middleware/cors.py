from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import get_settings


def add_cors_middleware(app: FastAPI):
    """
    Add CORS middleware to the FastAPI application.
    """
    settings = get_settings()
    
    # In production, replace "*" with specific origins
    origins = ["*"]  # This is for development; specify domains in production
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Expose headers that clients need access to
        expose_headers=["Access-Control-Allow-Origin"]
    )