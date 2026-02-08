from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
from datetime import datetime
import logging

# Import services and models
from src.services.rag_service import RAGService
from src.config.settings import Settings, get_settings
from src.utils.helpers import app_logger
from src.api.middleware.cors import add_cors_middleware
from src.utils.rate_limiter import add_rate_limiting

# Initialize database connection
from src.database.connection import neon_db

# Initialize the database connection when the module is loaded
try:
    neon_db.connect()
    print("Database connection initialized successfully")
except Exception as e:
    print(f"Error initializing database connection: {str(e)}")
    print("Application will start without database connection")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler to cleanup resources.
    """
    # Startup - nothing to do here since we already connected above
    yield  # This is where the application runs

    # Shutdown
    try:
        neon_db.disconnect()
        app_logger.info("Database connection closed successfully")
    except Exception as e:
        app_logger.error(f"Error closing database connection: {str(e)}")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="RAG Chatbot API",
    description="API for the Retrieval-Augmented Generation (RAG) chatbot that answers questions about book content",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
add_cors_middleware(app)

# Add rate limiting
add_rate_limiting(app)

# Include routers
from src.api.routes.chat import router as chat_router
from src.api.routes.health import router as health_router
from src.api.auth import router as auth_router
from src.api.user import router as user_router

app.include_router(chat_router)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(user_router)

# Add security headers
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Request/Response models
class SourceReference(BaseModel):
    chunk_id: str
    page_number: Optional[int]
    section_title: Optional[str]

class ChatResponse(BaseModel):
    response: str
    sources: List[SourceReference]
    confidence_score: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str

class IngestRequest(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None

# Dependency to get RAG service
def get_rag_service(settings: Settings = Depends(get_settings)):
    return RAGService(
        cohere_api_key=settings.cohere_api_key,
        qdrant_url=settings.qdrant_cluster_url,
        qdrant_api_key=settings.qdrant_api_key,
        neon_db_url=settings.neon_db_url
    )



@app.get("/")
async def root():
    """
    Root endpoint to verify the application is running.
    """
    app_logger.info("Root endpoint accessed")

    # Check database connectivity
    try:
        from sqlalchemy import text
        from src.database.connection import neon_db

        # Try to initialize connection if not already done
        if neon_db.engine is None:
            neon_db.connect()

        # Try to create a session to test the connection
        db = neon_db.get_session()
        db.execute(text("SELECT 1"))  # Simple test query using SQLAlchemy text()
        db.close()
        db_status = "Database connection successful"
    except Exception as e:
        app_logger.error(f"Database connection failed: {str(e)}")
        db_status = f"Database connection failed: {str(e)}"

    return {
        "message": "Backend API is running successfully",
        "database_status": db_status
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the application is running.
    """
    app_logger.info("Health check endpoint accessed")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/ingest")
async def ingest_endpoint(
    title: str,
    author: str,
    isbn: Optional[str] = None,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Ingest a book into the RAG system (admin-only endpoint).
    This is a simplified version - in practice, you'd handle file uploads differently.
    """
    try:
        app_logger.info(f"Starting book ingestion: {title} by {author}")

        # Validate inputs
        if not title or not author:
            raise HTTPException(status_code=400, detail="Title and author are required")

        # Ingest the book content using the RAG service
        book_id = await rag_service.ingest_book(
            title=title,
            author=author,
            isbn=isbn
        )

        app_logger.info(f"Successfully ingested book with ID: {book_id}")

        return {"message": "Book successfully ingested", "book_id": book_id}
    except Exception as e:
        app_logger.error(f"Error during book ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)