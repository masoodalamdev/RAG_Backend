"""
Final test script to verify the sign-in process
"""
import requests

# Test the login endpoint
api_base_url = "http://localhost:8000"

# Test data for login with the specific credentials mentioned
login_data = {
    "email": "masood@gmail.com",
    "password": "Kissing@2000"
}

print("Making sign-in request with masood@gmail.com and Kissing@2000...")
try:
    response = requests.post(f"{api_base_url}/api/auth/login", json=login_data)
    print(f"Sign-in request - Status: {response.status_code}")
    print(f"Sign-in response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Sign-in was successful!")
        response_data = response.json()
        access_token = response_data['token']['access_token']
        
        # Test accessing protected endpoint with the token
        print("\nTesting access to protected profile endpoint...")
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        profile_response = requests.get(f"{api_base_url}/api/user/profile", headers=headers)
        print(f"Profile access request - Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            print("✅ Profile access was successful!")
            print("✅ All authentication issues have been resolved!")
        else:
            print(f"❌ Profile access failed: {profile_response.text}")
    else:
        print(f"❌ Sign-in failed: {response.text}")
        
except Exception as e:
    print(f"❌ Request failed with error: {e}")