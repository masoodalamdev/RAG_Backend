from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, validator
from typing import Optional, List
import uuid
import time
import logging
from src.services.rag_service import RAGService, QueryResult
from src.config.settings import Settings, get_settings
from src.utils.helpers import api_logger
from src.utils.metrics import metrics_collector


router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    book_id: str
    selected_text: Optional[str] = None
    mode: str  # "full" or "selected"
    session_id: Optional[str] = None

    @validator('query')
    def validate_query(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Query cannot be empty')
        if len(v) > 1000:  # Limit query length
            raise ValueError('Query too long, must be less than 1000 characters')
        # Sanitize input to prevent injection attacks
        sanitized_v = v.replace('\0', '')  # Remove null bytes
        return sanitized_v

    @validator('book_id')
    def validate_book_id(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Invalid book_id format')

    @validator('mode')
    def validate_mode(cls, v):
        if v not in ["full", "selected"]:
            raise ValueError("Mode must be 'full' or 'selected'")
        return v

    @validator('selected_text')
    def validate_selected_text(cls, v, values):
        if v is not None and values.get('mode') == 'selected':
            if len(v) > 5000:  # Limit selected text length
                raise ValueError('Selected text too long, must be less than 5000 characters')
            # Sanitize input to prevent injection attacks
            sanitized_v = v.replace('\0', '')  # Remove null bytes
            return sanitized_v
        return v


class SourceReference(BaseModel):
    chunk_id: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[SourceReference]
    confidence_score: float


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    rag_service: RAGService = Depends(lambda: RAGService(
        cohere_api_key=get_settings().cohere_api_key,
        qdrant_url=get_settings().qdrant_cluster_url,
        qdrant_api_key=get_settings().qdrant_api_key,
        neon_db_url=get_settings().neon_db_url
    ))
):
    """
    Submit a query to the RAG chatbot and receive a response.
    """
    start_time = time.time()

    try:
        # Log the incoming request
        api_logger.info(f"Processing chat request for book_id: {request.book_id}, mode: {request.mode}")

        # Process the query using the RAG service
        result: QueryResult = await rag_service.process_query(
            query=request.query,
            book_id=request.book_id,
            selected_text=request.selected_text,
            mode=request.mode
        )

        # Log successful response
        api_logger.info(f"Successfully processed chat request for book_id: {request.book_id}")

        # Record metrics
        response_time = time.time() - start_time
        metrics_collector.record_response_time("/chat", response_time)
        metrics_collector.record_request("/chat")

        return ChatResponse(
            response=result.response_text,
            sources=result.sources,
            confidence_score=result.confidence_score
        )
    except HTTPException:
        # Record error metric
        response_time = time.time() - start_time
        metrics_collector.record_response_time("/chat", response_time)
        metrics_collector.record_error("/chat")

        # Re-raise HTTP exceptions as-is
        api_logger.error(f"HTTP exception in chat endpoint: {request.book_id}")
        raise
    except ValueError as ve:
        # Record error metric
        response_time = time.time() - start_time
        metrics_collector.record_response_time("/chat", response_time)
        metrics_collector.record_error("/chat")

        # Handle validation errors
        api_logger.warning(f"Validation error in chat endpoint: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Record error metric
        response_time = time.time() - start_time
        metrics_collector.record_response_time("/chat", response_time)
        metrics_collector.record_error("/chat")

        # Log the error and return a generic error response
        api_logger.error(f"Error processing chat request for book_id {request.book_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")