"""
Test script to simulate the registration API call
"""
import requests
import json

# Test the registration endpoint
api_base_url = "http://localhost:8000"

# Test data for registration
registration_data = {
    "email": "test_api_new@example.com",
    "password": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User",
    "software_background": {
        "languages": ["Python", "JavaScript"],
        "frameworks": ["FastAPI", "React"],
        "experience_years": 5
    },
    "hardware_background": {
        "devices": ["Laptop", "Desktop"],
        "os_preference": "Linux",
        "setup_description": "Dual monitor setup"
    }
}

print("Making first registration request...")
try:
    response = requests.post(f"{api_base_url}/api/auth/register", json=registration_data)
    print(f"First request - Status: {response.status_code}")
    print(f"First request - Response: {response.text}")
except Exception as e:
    print(f"First request failed: {e}")

print("\nMaking second registration request with same email...")
try:
    response = requests.post(f"{api_base_url}/api/auth/register", json=registration_data)
    print(f"Second request - Status: {response.status_code}")
    print(f"Second request - Response: {response.text}")
except Exception as e:
    print(f"Second request failed: {e}")