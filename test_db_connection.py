import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv("NEON_DB_URL")
print(f"Database URL: {DATABASE_URL}")

if DATABASE_URL:
    try:
        # Create sync engine
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,    # Recycle connections every 5 minutes
            echo=True  # Enable for debugging
        )
        
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            print(f"Result: {result.fetchone()}")
    except Exception as e:
        print(f"Database connection failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("DATABASE_URL is not set")