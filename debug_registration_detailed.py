"""
Detailed debug script to trace the registration issue
"""
import asyncio
import os
import sys
import logging
sys.path.insert(0, os.path.abspath('.'))

# Set up logging to see detailed information
logging.basicConfig(level=logging.DEBUG)

# Initialize the database connection first
from src.database.connection import neon_db
try:
    neon_db.connect()
    print("Database connection initialized successfully")
except Exception as e:
    print(f"Error initializing database connection: {str(e)}")
    print("Application will start without database connection")

from src.services.auth_service import AuthService
from src.models.auth import RegisterRequest

async def test_registration_detailed():
    # Create a sample registration request
    register_request = RegisterRequest(
        email="test_debug@example.com",  # Using a different email to avoid previous test data
        password="SecurePassword123!",
        first_name="Test",
        last_name="User",
        software_background={
            "languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React"],
            "experience_years": 5
        },
        hardware_background={
            "devices": ["Laptop", "Desktop"],
            "os_preference": "Linux",
            "setup_description": "Dual monitor setup"
        }
    )
    
    auth_service = AuthService()
    
    print("=== Starting first registration ===")
    try:
        result = await auth_service.register_user(register_request)
        print(f"First registration result: {result}")
    except Exception as e:
        print(f"First registration failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Checking if user exists in DB directly ===")
    try:
        # Check directly in the database
        from sqlalchemy import text
        db = neon_db.get_session()
        
        # Query for the user
        result = db.execute(text("SELECT id, email FROM \"user\" WHERE email = :email"), {"email": "test_debug@example.com"})
        user_row = result.fetchone()
        
        if user_row:
            print(f"User found in DB: ID={user_row[0]}, Email={user_row[1]}")
        else:
            print("User not found in DB")
            
        db.close()
    except Exception as e:
        print(f"Error checking DB: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Starting second registration with same email ===")
    try:
        result = await auth_service.register_user(register_request)
        print(f"Second registration result: {result}")
    except Exception as e:
        print(f"Second registration failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_registration_detailed())