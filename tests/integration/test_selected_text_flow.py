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
async def test_selected_text_query_flow_integration(client, mock_rag_service):
    """Test the complete selected text query flow from API to service."""
    # Mock the RAG service response
    mock_response = QueryResult(
        response_text="This is a response based on the selected text.",
        sources=[],
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
    assert len(response_data["sources"]) == 0  # No sources for selected text mode
    assert response_data["confidence_score"] == 0.85
    
    # Verify the service was called with correct parameters
    mock_rag_service.process_query.assert_called_once_with(
        query="Explain this concept",
        book_id="123e4567-e89b-12d3-a456-426614174000",
        selected_text="The concept of machine learning involves algorithms that improve through experience.",
        mode="selected"
    )


@pytest.mark.asyncio
async def test_selected_text_query_with_empty_text(client, mock_rag_service):
    """Test the selected text query flow with empty selected text."""
    # Mock the RAG service response
    mock_response = QueryResult(
        response_text="No selected text provided, using full book mode.",
        sources=[
            SourceReference(
                chunk_id="chunk-123",
                page_number=15,
                section_title="Introduction"
            )
        ],
        confidence_score=0.75
    )
    mock_rag_service.process_query.return_value = mock_response
    
    # Make a request to the API with empty selected text
    request_data = {
        "query": "Explain this concept",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "selected_text": "",
        "mode": "selected"
    }
    
    response = client.post("/chat", json=request_data)
    
    # Verify the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["response"] == "No selected text provided, using full book mode."
    assert len(response_data["sources"]) == 1
    assert response_data["confidence_score"] == 0.75
    
    # Verify the service was called with correct parameters
    mock_rag_service.process_query.assert_called_once_with(
        query="Explain this concept",
        book_id="123e4567-e89b-12d3-a456-426614174000",
        selected_text="",
        mode="selected"
    )