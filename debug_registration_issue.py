"""
Debug script to test the registration issue
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

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

async def test_registration():
    # Create a sample registration request
    register_request = RegisterRequest(
        email="test@example.com",
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
    
    print("Attempting first registration...")
    try:
        result = await auth_service.register_user(register_request)
        print(f"First registration result: {result}")
    except Exception as e:
        print(f"First registration failed with error: {e}")
    
    print("\nAttempting second registration with same email...")
    try:
        result = await auth_service.register_user(register_request)
        print(f"Second registration result: {result}")
    except Exception as e:
        print(f"Second registration failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_registration())