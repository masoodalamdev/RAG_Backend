import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.api.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")