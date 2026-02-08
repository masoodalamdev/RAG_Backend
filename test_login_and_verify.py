"""
Test script to verify the login and token workflow end-to-end
"""
import requests
import os
from jose import jwt, JWTError
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Load the secret key from environment
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "fallback_secret_key_for_development")
ALGORITHM = "HS256"

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
        print(f"User ID: {response_data['user_id']}")
        print(f"Email: {response_data['email']}")
        
        # Get the token from the response
        token_data = response_data['token']
        access_token = token_data['access_token']
        print(f"Access token: {access_token}")
        
        # Now try to verify the token immediately
        print("\nVerifying the received token...")
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"Token verification successful: {payload}")
            
            user_id = payload.get("sub")
            print(f"User ID from token: {user_id}")
            
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                current_time = datetime.now(timezone.utc)
                print(f"Token expiration: {exp_datetime}")
                print(f"Current time: {current_time}")
                print(f"Token expired: {current_time > exp_datetime}")
                
        except JWTError as e:
            print(f"JWT Error decoding token: {e}")
            print("This explains the 'Invalid or expired token' error!")
        except Exception as e:
            print(f"Other error decoding token: {e}")
    else:
        print(f"Login failed: {response.text}")
        
except Exception as e:
    print(f"Login request failed: {e}")