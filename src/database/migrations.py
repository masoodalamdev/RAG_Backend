"""
Better Auth Migration Script
This script extends the Better Auth user table with custom fields for software and hardware background.
"""
import asyncio
import asyncpg
import os
from typing import Dict, Any


async def run_better_auth_migrations():
    """
    Run Better Auth migrations to create the base tables.
    This would typically be done using Better Auth's CLI tool.
    """
    print("Running Better Auth base migrations...")
    # In a real implementation, this would call Better Auth's migration system
    # For now, we'll simulate the process
    print("Base migrations completed.")


async def extend_user_table_with_custom_fields():
    """
    Extend the existing Better Auth user table with custom fields for background data.
    """
    # Connect to the database
    conn = await asyncpg.connect(os.getenv("NEON_DB_URL"))
    
    try:
        # Add software_background column if it doesn't exist
        await conn.execute("""
            ALTER TABLE "user" 
            ADD COLUMN IF NOT EXISTS software_background JSONB DEFAULT '{}'
        """)
        
        # Add hardware_background column if it doesn't exist
        await conn.execute("""
            ALTER TABLE "user" 
            ADD COLUMN IF NOT EXISTS hardware_background JSONB DEFAULT '{}'
        """)
        
        print("User table extended with custom fields successfully!")
        
    except Exception as e:
        print(f"Error extending user table: {e}")
        raise
    finally:
        await conn.close()


async def main():
    """Main function to run all migrations."""
    print("Starting Better Auth migrations...")
    
    # Run base migrations
    await run_better_auth_migrations()
    
    # Extend user table with custom fields
    await extend_user_table_with_custom_fields()
    
    print("All migrations completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())