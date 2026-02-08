"""
Authentication Configuration
"""
import os
from typing import Optional
from pydantic import BaseModel
from jose import jwt, JWTError
from src.database.connection import neon_db
from src.models.user_model import User
from sqlalchemy.orm import Session
import bcrypt


# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_development")
ALGORITHM = "HS256"


class SoftwareBackground(BaseModel):
    """Software background information for user profiles."""
    languages: list[str] = []
    frameworks: list[str] = []
    experience_years: int = 0


class HardwareBackground(BaseModel):
    """Hardware background information for user profiles."""
    devices: list[str] = []
    os_preference: str = ""
    setup_description: str = ""


def get_current_user(token: str = None) -> Optional[dict]:
    """
    Get the current authenticated user from the token.

    Args:
        token: JWT token from Authorization header

    Returns:
        User dictionary if valid, None otherwise
    """
    if not token:
        return None

    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        # Get database session
        db = neon_db.get_session()
        try:
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                return None

            # Return user data
            return {
                "id": str(user.id),
                "email": user.email,
                "software_background": user.software_background,
                "hardware_background": user.hardware_background
            }
        finally:
            db.close()
    except JWTError:
        return None