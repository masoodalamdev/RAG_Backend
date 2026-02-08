from src.database.connection import neon_db
from src.models.user_model import User
from sqlalchemy import inspect

# Connect to the database
neon_db.connect()

# Create a session
db = neon_db.get_session()

# Check if the user table exists
inspector = inspect(neon_db.engine)
table_names = inspector.get_table_names()

print(f"Tables in the database: {table_names}")

if 'user' in table_names:
    print("User table exists")
    
    # Get column information
    columns = inspector.get_columns('user')
    print("User table columns:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")
else:
    print("User table does NOT exist")

# Close the session
db.close()