import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    
    # Check status code
    assert response.status_code == 200
    
    # Check response structure
    response_data = response.json()
    assert "status" in response_data
    assert "timestamp" in response_data
    
    # Check values
    assert response_data["status"] == "healthy"
    assert isinstance(response_data["timestamp"], str)
    
    # Check timestamp format (ISO format)
    import datetime
    try:
        datetime.datetime.fromisoformat(response_data["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        assert False, "Timestamp is not in valid ISO format"


def test_health_endpoint_post_not_allowed(client):
    """Test that POST requests to /health are not allowed."""
    response = client.post("/health")
    
    # Should return 405 Method Not Allowed
    assert response.status_code == 405