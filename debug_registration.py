import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.services.auth_service import AuthService
from src.models.auth import RegisterRequest
from src.database.connection import neon_db

async def test_registration():
    print("Connecting to database...")
    try:
        neon_db.connect()
        print("Database connection successful")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return
    
    print("Creating auth service...")
    auth_service = AuthService()
    
    print("Creating registration request...")
    register_request = RegisterRequest(
        email="debug_test@example.com",
        password="TestPass123!",
        software_background={
            "languages": ["Python", "JavaScript"],
            "frameworks": ["React", "FastAPI"],
            "experience_years": 3
        },
        hardware_background={
            "devices": ["Laptop", "Raspberry Pi"],
            "os_preference": "Linux",
            "setup_description": "Development workstation"
        }
    )
    
    print("Calling register_user...")
    try:
        result = await auth_service.register_user(register_request)
        print(f"Registration result: {result}")
    except Exception as e:
        print(f"Error during registration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_registration())