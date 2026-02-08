"""
Database Migration Script
This script creates the user table with custom fields for software and hardware background.
"""
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from src.database.connection import neon_db
from src.models.user_model import User
from src.models.base import Base


def run_sqlalchemy_migrations():
    """
    Run SQLAlchemy migrations to create tables with custom fields.
    """
    try:
        # Create all tables defined in models
        engine = create_engine(os.getenv("NEON_DB_URL"))
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
        # Verify the user table has the custom columns
        with engine.connect() as conn:
            # Check if software_background column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'software_background'
            """))
            if not result.fetchone():
                print("Adding software_background column...")
                conn.execute(text("""
                    ALTER TABLE "user" ADD COLUMN IF NOT EXISTS software_background JSONB DEFAULT '{}'
                """))
                
            # Check if hardware_background column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'hardware_background'
            """))
            if not result.fetchone():
                print("Adding hardware_background column...")
                conn.execute(text("""
                    ALTER TABLE "user" ADD COLUMN IF NOT EXISTS hardware_background JSONB DEFAULT '{}'
                """))
            
            conn.commit()
        
        print("User table extended with custom fields successfully!")

    except Exception as e:
        print(f"Error during migrations: {e}")
        raise


def main():
    """Main function to run all migrations."""
    print("Starting database migrations...")
    
    # Run SQLAlchemy migrations
    run_sqlalchemy_migrations()
    
    print("All migrations completed successfully!")


if __name__ == "__main__":
    main()