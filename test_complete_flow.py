"""
Test script to verify the complete login and profile access workflow
"""
import requests
import os
from jose import jwt, JWTError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    
    if response.status_code == 200:
        response_data = response.json()
        print(f"Login successful!")
        
        # Get the token from the response
        access_token = response_data['token']['access_token']
        print(f"Received access token")
        
        # Now try to access the user profile with the token
        print("\nTrying to access user profile with the token...")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        profile_response = requests.get(f"{api_base_url}/api/user/profile", headers=headers)
        print(f"Profile request - Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"Profile access successful!")
            print(f"User ID: {profile_data['id']}")
            print(f"Email: {profile_data['email']}")
            print(f"Software background: {profile_data['software_background']}")
            print(f"Hardware background: {profile_data['hardware_background']}")
        else:
            print(f"Profile access failed: {profile_response.text}")
    else:
        print(f"Login failed: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")