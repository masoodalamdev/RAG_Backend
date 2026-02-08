"""
Test script to debug the token verification issue
"""
import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Load the secret key from environment
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "fallback_secret_key_for_development")
ALGORITHM = "HS256"

# Test token from the login response
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlNDFkZGE5NC01ZTBhLTRjNmItODE4Zi0zOGJmN2I1MWNjMmEiLCJleHAiOjE3NzA1MzQ2NjZ9.j92lJw7yINQC3Tgor8U19UfRpA_FjaiWtxQKC_tFWhU"

print(f"Using SECRET_KEY: {SECRET_KEY}")
print(f"Test token: {test_token}")

try:
    # Decode the token
    payload = jwt.decode(test_token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"Token decoded successfully: {payload}")
    
    user_id = payload.get("sub")
    print(f"User ID from token: {user_id}")
    
    exp_timestamp = payload.get("exp")
    print(f"Expiration timestamp: {exp_timestamp}")
    
    # Check if token is expired
    if exp_timestamp:
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        current_time = datetime.now(timezone.utc)
        print(f"Token expiration: {exp_datetime}")
        print(f"Current time: {current_time}")
        print(f"Token expired: {current_time > exp_datetime}")
    
except JWTError as e:
    print(f"JWT Error decoding token: {e}")
except Exception as e:
    print(f"Other error decoding token: {e}")