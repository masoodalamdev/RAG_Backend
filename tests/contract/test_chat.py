import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


def test_chat_endpoint_contract(client):
    """Test the /chat endpoint contract."""
    # Test valid request
    valid_request = {
        "query": "What is the main concept discussed in the book?",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "mode": "full"
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


def test_chat_endpoint_invalid_mode(client):
    """Test the /chat endpoint with invalid mode."""
    invalid_request = {
        "query": "What is the main concept discussed in the book?",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "mode": "invalid_mode"
    }
    
    response = client.post("/chat", json=invalid_request)
    
    # Should return 400 for invalid mode
    assert response.status_code == 400


def test_chat_endpoint_missing_fields(client):
    """Test the /chat endpoint with missing required fields."""
    incomplete_request = {
        "query": "What is the main concept discussed in the book?"
        # Missing book_id and mode
    }
    
    response = client.post("/chat", json=incomplete_request)
    
    # Should return 422 for validation error
    assert response.status_code == 422