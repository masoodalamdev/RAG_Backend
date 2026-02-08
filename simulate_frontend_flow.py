"""
Test script to simulate the frontend login flow
"""
import requests

# Step 1: Login and get token
api_base_url = "http://localhost:8000"

login_data = {
    "email": "masood@gmail.com",
    "password": "Kissing@2000"
}

print("Step 1: Logging in...")
login_response = requests.post(f"{api_base_url}/api/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    login_data_response = login_response.json()
    access_token = login_data_response['token']['access_token']
    print(f"Received access token: {access_token[:20]}...")  # Show first 20 chars
    
    print("\nStep 2: Accessing profile with the token...")
    # Simulate how the frontend would make the profile request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    profile_response = requests.get(f"{api_base_url}/api/user/profile", headers=headers)
    print(f"Profile request status: {profile_response.status_code}")
    print(f"Profile response: {profile_response.text}")
else:
    print(f"Login failed: {login_response.text}")