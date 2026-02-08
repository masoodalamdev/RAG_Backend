"""
Database connection module for Neon Postgres
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("NEON_DB_URL")


class NeonDB:
    """Neon Postgres database connection class"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """Initialize the database connection"""
        # Create sync engine (since the auth service uses sync operations)
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,    # Recycle connections every 5 minutes
            echo=True  # Enable for debugging
        )

        # Create session maker
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=Session,
            expire_on_commit=False
        )

    def disconnect(self):
        """Close the database connection"""
        if self.engine:
            self.engine.dispose()

    def get_session(self):
        """Get a database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.SessionLocal()


# Create global instance
neon_db = NeonDB(DATABASE_URL)


@contextmanager
def get_db_session_context():
    """Context manager to get database session"""
    db = neon_db.get_session()
    try:
        yield db
    finally:
        db.close()