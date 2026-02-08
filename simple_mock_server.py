from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import uuid
import random
import time
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Simple Mock RAG Chatbot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"],  # Allow specific origins
    allow_credentials=False,  # Set to False to allow wildcard origins
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Simple models without validators
class SourceReference(BaseModel):
    chunk_id: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    book_id: str
    selected_text: Optional[str] = None
    mode: str = "full"  # Default to "full"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[SourceReference]
    confidence_score: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str

@app.get("/")
async def root():
    return {"message": "Simple Mock Backend API is running successfully"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Simple mock endpoint that simulates the RAG chatbot response.
    """
    try:
        # Simulate processing delay
        time.sleep(0.1)
        
        # Generate a mock response based on the query
        query_lower = request.query.lower()
        
        if "physical ai" in query_lower or "humanoid" in query_lower:
            response = (
                "Physical AI refers to the integration of artificial intelligence with physical systems, "
                "particularly in robotics. In the context of humanoid robotics, Physical AI encompasses "
                "the algorithms and systems that enable human-like robots to perceive, reason, and act "
                "in physical environments. This includes sensorimotor learning, embodied cognition, "
                "and the tight coupling between perception and action."
            )
        elif "ros" in query_lower:
            response = (
                "ROS (Robot Operating System) 2 is a flexible framework for writing robot software. "
                "It's a collection of tools, libraries, and conventions that aim to simplify the task "
                "of creating complex and robust robot behavior across a wide variety of robotic platforms. "
                "ROS 2 addresses limitations of the original ROS and provides improved security, "
                "real-time capabilities, and better cross-platform support."
            )
        elif "vision" in query_lower or "action" in query_lower:
            response = (
                "Vision-Language-Action systems integrate computer vision, natural language processing, "
                "and motor control to enable robots to understand and interact with their environment "
                "based on visual input and linguistic commands. These systems allow robots to perform "
                "complex tasks by combining perception, reasoning, and action in a unified framework."
            )
        elif "digital twin" in query_lower or "gazebo" in query_lower:
            response = (
                "Digital twins in robotics refer to virtual replicas of physical robots or robotic systems. "
                "Platforms like Gazebo and Unity provide physics-based simulation environments where "
                "robots can be tested and trained before deployment in the real world. This approach "
                "allows for safer, faster, and more cost-effective development of robotic systems."
            )
        else:
            response = (
                f"I can help answer questions about Physical AI and Humanoid Robotics. "
                f"Based on your query '{request.query}', I can tell you that this topic is covered "
                f"in the Physical AI & Humanoid Robotics book. The book covers modules on ROS 2, "
                f"Digital Twins, AI Robot Brains, and Vision-Language-Action Systems."
            )
        
        # Generate mock sources
        sources = []
        for i in range(min(3, random.randint(1, 3))):
            sources.append(SourceReference(
                chunk_id=f"chunk_{uuid.uuid4().hex[:8]}",
                page_number=random.randint(10, 200),
                section_title=f"Section {random.randint(1, 10)}.{random.randint(1, 5)}"
            ))
        
        # Generate confidence score
        confidence_score = round(random.uniform(0.7, 0.95), 2)
        
        return ChatResponse(
            response=response,
            sources=sources,
            confidence_score=confidence_score
        )
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")  # This will help us debug
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)