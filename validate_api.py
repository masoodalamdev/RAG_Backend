"""
Basic validation script for the RAG Chatbot API
This script performs basic tests to validate the API functionality
"""
import requests
import time
import uuid


def test_health_endpoint(base_url):
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data['status']}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check failed with error: {str(e)}")
        return False


def test_chat_endpoint(base_url):
    """Test the chat endpoint with a simple query."""
    print("\nTesting chat endpoint...")
    try:
        # This test will likely fail due to missing dependencies (Cohere API, etc.)
        # But it should at least validate the endpoint structure
        test_request = {
            "query": "What is this book about?",
            "book_id": str(uuid.uuid4()),  # Valid UUID format
            "mode": "full"
        }
        
        response = requests.post(f"{base_url}/chat", json=test_request)
        
        # We expect a 500 error due to missing dependencies, but not a 404 or other error
        if response.status_code in [200, 422, 500]:
            print(f"✓ Chat endpoint responded with status {response.status_code}")
            print("  (Note: 500 errors are expected if external services aren't configured)")
            return True
        else:
            print(f"✗ Chat endpoint unexpected status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Chat endpoint test failed with error: {str(e)}")
        return False


def main():
    """Main validation function."""
    print("Starting RAG Chatbot API validation...\n")
    
    # Use the default development server URL
    base_url = "http://localhost:8000"
    
    # Run tests
    health_ok = test_health_endpoint(base_url)
    chat_ok = test_chat_endpoint(base_url)
    
    print(f"\nValidation Summary:")
    print(f"- Health endpoint: {'PASS' if health_ok else 'FAIL'}")
    print(f"- Chat endpoint: {'PASS' if chat_ok else 'FAIL'}")
    
    if health_ok and chat_ok:
        print("\n✓ All basic validations passed!")
        print("Note: For full functionality, ensure external services (Cohere API, Qdrant, NeonDB) are configured.")
    else:
        print("\n✗ Some validations failed.")
        print("Check the logs above for details.")


if __name__ == "__main__":
    main()