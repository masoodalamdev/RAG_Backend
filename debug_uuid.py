from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import uuid

app = FastAPI()

class ChatRequest(BaseModel):
    query: str
    book_id: str
    mode: str

@app.post("/test")
async def test_endpoint(request: ChatRequest):
    # Validate book_id is a UUID
    try:
        uuid.UUID(request.book_id)
    except ValueError:
        return {"error": "Invalid UUID format"}
    
    return {"message": "Valid request", "received": request.dict()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)