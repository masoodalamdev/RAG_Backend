"""
Debug script to test the user profile retrieval directly
"""
import asyncio
import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))

# Initialize the database connection first
from src.database.connection import neon_db
try:
    neon_db.connect()
    print("Database connection initialized successfully")
except Exception as e:
    print(f"Error initializing database connection: {str(e)}")

from src.services.auth_service import AuthService

async def test_get_user_profile():
    auth_service = AuthService()
    
    # Use the user ID from our previous tests
    user_id = "e41dda94-5e0a-4c6b-818f-38bf7b51cc2a"
    
    print(f"Attempting to retrieve profile for user ID: {user_id}")
    try:
        result = await auth_service.get_user_profile(user_id)
        print(f"Profile retrieval result: {result}")
        
        if result:
            print(f"Result type: {type(result)}")
            print(f"Keys: {result.keys() if hasattr(result, 'keys') else 'N/A'}")
            
            # Try to serialize it to JSON to see if there are any issues
            try:
                json_result = json.dumps(result, default=str)  # Use default=str to handle datetime
                print("JSON serialization successful")
            except Exception as e:
                print(f"JSON serialization failed: {e}")
        else:
            print("Profile retrieval returned None")
    except Exception as e:
        print(f"Profile retrieval failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_get_user_profile())