"""
User profile API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from src.models.auth import UserProfileResponse
from src.services.auth_service import AuthService
from src.config.auth_config import get_current_user
from src.models.user import UserUpdate  # Assuming this is the correct import for UserUpdate


def get_auth_service():
    """Dependency to get auth service instance."""
    return AuthService()


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["User Profile"])
security = HTTPBearer()


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get the authenticated user's profile information.
    """
    try:
        token = credentials.credentials
        user_data = await auth_service.verify_token(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_id = user_data.get("id") if isinstance(user_data, dict) else getattr(user_data, "id", None)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID found"
            )
        
        profile = await auth_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UserProfileResponse(
            id=profile["id"],
            email=profile["email"],
            created_at=profile["created_at"],
            updated_at=profile["updated_at"],
            software_background=profile["software_background"],
            hardware_background=profile["hardware_background"]
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving profile"
        )


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update the authenticated user's profile information.
    """
    try:
        token = credentials.credentials
        user_data = await auth_service.verify_token(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_id = user_data.get("id") if isinstance(user_data, dict) else getattr(user_data, "id", None)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID found"
            )
        
        updated_profile = await auth_service.update_user_profile(user_id, profile_update)
        
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user profile"
            )
        
        return UserProfileResponse(
            id=updated_profile["id"],
            email=updated_profile["email"],
            created_at=updated_profile["created_at"],
            updated_at=updated_profile["updated_at"],
            software_background=updated_profile["software_background"],
            hardware_background=updated_profile["hardware_background"]
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error updating profile"
        )