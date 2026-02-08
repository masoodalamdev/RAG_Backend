import asyncio
import aiohttp
import json

async def test_chat_api():
    """Test the chat API endpoint"""
    url = "http://localhost:8000/chat"
    
    # Sample request data
    data = {
        "query": "What is Physical AI?",
        "book_id": "123e4567-e89b-12d3-a456-426614174000",  # Valid UUID format
        "mode": "full"
    }
    
    print("Testing chat API endpoint...")
    print(f"Sending request to: {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"Response: {json.dumps(result, indent=2)}")
                    print("\n[SUCCESS] Chat API test successful!")
                else:
                    error_text = await response.text()
                    print(f"[ERROR] Error response: {error_text}")

    except Exception as e:
        print(f"[ERROR] Error connecting to API: {str(e)}")
        print("Make sure the backend server is running on http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(test_chat_api())