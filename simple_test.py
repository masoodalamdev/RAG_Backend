import requests
import json

# Test the root endpoint
try:
    response = requests.get("http://localhost:8000/")
    print(f"Root endpoint status: {response.status_code}")
    print(f"Root endpoint response: {response.json()}")
except Exception as e:
    print(f"Error accessing root endpoint: {e}")

# Test the health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    print(f"Health endpoint status: {response.status_code}")
    print(f"Health endpoint response: {response.json()}")
except Exception as e:
    print(f"Error accessing health endpoint: {e}")

# Test the chat endpoint with the exact format from the original code
try:
    data = {
        "query": "What is Physical AI?",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "mode": "full"
    }
    response = requests.post("http://localhost:8000/chat", json=data)
    print(f"Chat endpoint status: {response.status_code}")
    if response.status_code != 200:
        print(f"Chat endpoint error: {response.text}")
        # Let's also try with a session_id to match the original model
        data_with_session = data.copy()
        data_with_session["session_id"] = "test-session-id"
        response2 = requests.post("http://localhost:8000/chat", json=data_with_session)
        print(f"Chat endpoint with session_id status: {response2.status_code}")
        if response2.status_code != 200:
            print(f"Chat endpoint with session_id error: {response2.text}")
        else:
            print(f"Chat endpoint with session_id response: {response2.json()}")
    else:
        print(f"Chat endpoint response: {response.json()}")
except Exception as e:
    print(f"Error accessing chat endpoint: {e}")

# Test the chat endpoint with minimal data
try:
    data = {
        "query": "What is Physical AI?",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",
        "mode": "full"
    }
    response = requests.post("http://localhost:8000/chat", json=data)
    print(f"Chat endpoint status: {response.status_code}")
    if response.status_code != 200:
        print(f"Chat endpoint error: {response.text}")
    else:
        print(f"Chat endpoint response: {response.json()}")
except Exception as e:
    print(f"Error accessing chat endpoint: {e}")