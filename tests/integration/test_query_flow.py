import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.api.main import app
from src.services.rag_service import RAGService, QueryResult
from src.services.rag_service import SourceReference


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_rag_service():
    """Create a mock RAG service."""
    with patch('src.api.main.get_rag_service') as mock_get_service:
        mock_service = AsyncMock(spec=RAGService)
        mock_get_service.return_value = mock_service
        yield mock_service


@pytest.mark.asyncio
async def test_user_query_flow_integration(client, mock_rag_service):
    """Test the complete user query flow from API to service."""
    # Mock the RAG service response
    mock_response = QueryResult(
        response_text="This is a test response based on the book content.",
        sources=[
            SourceReference(
                chunk_id="chunk-123",
                page_number=15,
                section_title="Introduction"
            )
        ],
        confidence_score=0.92
    )
    mock_rag_service.process_query.return_value = mock_response
    
    # Make a request to the API
    request_data = {
        "query": "What is the main concept discussed in the book?",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "mode": "full"
    }
    
    response = client.post("/chat", json=request_data)
    
    # Verify the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["response"] == "This is a test response based on the book content."
    assert len(response_data["sources"]) == 1
    assert response_data["confidence_score"] == 0.92
    
    # Verify the service was called with correct parameters
    mock_rag_service.process_query.assert_called_once_with(
        query="What is the main concept discussed in the book?",
        book_id="123e4567-e89b-12d3-a456-426614174000",
        selected_text=None,
        mode="full"
    )


@pytest.mark.asyncio
async def test_user_query_flow_with_selected_text(client, mock_rag_service):
    """Test the user query flow with selected text."""
    # Mock the RAG service response
    mock_response = QueryResult(
        response_text="This is a response based on the selected text.",
        sources=[
            SourceReference(
                chunk_id="chunk-456",
                page_number=25,
                section_title="Chapter 1"
            )
        ],
        confidence_score=0.85
    )
    mock_rag_service.process_query.return_value = mock_response
    
    # Make a request to the API with selected text
    request_data = {
        "query": "Explain this concept",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "selected_text": "The concept of machine learning involves algorithms that improve through experience.",
        "mode": "selected"
    }
    
    response = client.post("/chat", json=request_data)
    
    # Verify the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["response"] == "This is a response based on the selected text."
    assert len(response_data["sources"]) == 1
    assert response_data["confidence_score"] == 0.85
    
    # Verify the service was called with correct parameters
    mock_rag_service.process_query.assert_called_once_with(
        query="Explain this concept",
        book_id="123e4567-e89b-12d3-a456-426614174000",
        selected_text="The concept of machine learning involves algorithms that improve through experience.",
        mode="selected"
    )