"""
Dependencies module for authentication.

This module contains dependency functions for protecting routes with authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from .auth import get_current_user, get_db
from ..models.user_model import User


# Initialize security scheme
security = HTTPBearer()


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current active user.
    
    This raises an exception if the user is not authenticated.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user