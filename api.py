from mangum import Mangum
from src.api.main import app

# This creates a handler for Vercel's serverless environment
handler = Mangum(app)

# Make sure the FastAPI app instance is available as 'app'
# This is what Vercel looks for in FastAPI applications
app = app