import requests
import json
from datetime import datetime

# Test registration
url = "http://localhost:8000/api/auth/register"

# Sample registration data
registration_data = {
    "email": f"test_{int(datetime.now().timestamp())}@example.com",
    "password": "TestPass123!",
    "software_background": {
        "languages": ["Python", "JavaScript"],
        "frameworks": ["React", "FastAPI"],
        "experience_years": 3
    },
    "hardware_background": {
        "devices": ["Laptop", "Raspberry Pi"],
        "os_preference": "Linux",
        "setup_description": "Development workstation"
    }
}

try:
    print("Attempting to register user...")
    print(f"Sending data: {json.dumps(registration_data, indent=2)}")
    
    response = requests.post(url, json=registration_data)
    
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("\nRegistration successful!")
    else:
        print(f"\nRegistration failed with status code: {response.status_code}")
        
except Exception as e:
    print(f"Error during registration test: {e}")