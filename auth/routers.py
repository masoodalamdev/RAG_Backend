"""
User router module for profile endpoints.

This module contains endpoints for viewing and updating user profiles.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from ..models.user_model import User
from .auth import (
    UserResponse, 
    UserUpdateRequest, 
    get_current_user, 
    get_db, 
    hash_password
)
from .dependencies import get_current_active_user


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's profile information.
    
    This endpoint returns the profile information for the authenticated user,
    including their background information.
    """
    # Return the user data as a response
    return UserResponse.from_orm(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile information.
    
    This endpoint allows authenticated users to update their profile information,
    including their background information.
    """
    # Update user fields if provided
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    if user_update.software_background is not None:
        current_user.software_background = user_update.software_background.dict()
    if user_update.hardware_background is not None:
        current_user.hardware_background = user_update.hardware_background.dict()

    # Commit changes to the database
    db.commit()
    db.refresh(current_user)

    # Return updated user data
    return UserResponse.from_orm(current_user)