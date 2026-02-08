"""
Test script to debug the login issue
"""
import requests
import json

# Test the login endpoint
api_base_url = "http://localhost:8000"

# Test data for login
login_data = {
    "email": "masood@gmail.com",
    "password": "Kissing@2000"
}

print("Making login request...")
try:
    response = requests.post(f"{api_base_url}/api/auth/login", json=login_data)
    print(f"Login request - Status: {response.status_code}")
    print(f"Login request - Response: {response.text}")
except Exception as e:
    print(f"Login request failed: {e}")