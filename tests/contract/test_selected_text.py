import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


def test_chat_endpoint_with_selected_text(client):
    """Test the /chat endpoint with selected text."""
    # Test valid request with selected text
    valid_request = {
        "query": "Explain this concept",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "selected_text": "The concept of machine learning involves algorithms that improve through experience.",
        "mode": "selected"
    }
    
    response = client.post("/chat", json=valid_request)
    
    # Check status code
    assert response.status_code == 200
    
    # Check response structure
    response_data = response.json()
    assert "response" in response_data
    assert "sources" in response_data
    assert "confidence_score" in response_data
    
    # Check data types
    assert isinstance(response_data["response"], str)
    assert isinstance(response_data["sources"], list)
    assert isinstance(response_data["confidence_score"], float)
    
    # Check confidence score range
    assert 0.0 <= response_data["confidence_score"] <= 1.0


def test_chat_endpoint_full_mode_with_selected_text(client):
    """Test the /chat endpoint in full mode with selected text provided."""
    # Test request with selected text but mode is full
    request_data = {
        "query": "What is the main concept discussed in the book?",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "selected_text": "The concept of machine learning involves algorithms that improve through experience.",
        "mode": "full"
    }
    
    response = client.post("/chat", json=request_data)
    
    # Should return 200 as selected text is ignored in full mode
    assert response.status_code == 200


def test_chat_endpoint_selected_mode_without_selected_text(client):
    """Test the /chat endpoint in selected mode without selected text."""
    # Test request with selected mode but no selected text
    request_data = {
        "query": "Explain this concept",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "selected_text": None,
        "mode": "selected"
    }
    
    response = client.post("/chat", json=request_data)
    
    # Should return 200, but the service should handle the lack of selected text appropriately
    assert response.status_code == 200