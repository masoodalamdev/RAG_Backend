"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from pydantic import BaseModel

from src.models.auth import RegisterRequest, LoginRequest, RegisterResponse, LoginResponse
from src.services.auth_service import AuthService
from src.config.auth_config import get_current_user
# Note: The User model is not directly used in this auth.py file, so we can remove this import
# or keep it if it's used elsewhere. For now, I'll comment it out.
# from src.models.user import User
from slowapi import Limiter
from slowapi.util import get_remote_address


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

# Initialize rate limiter for auth endpoints
limiter = Limiter(key_func=get_remote_address)


def get_auth_service():
    """Dependency to get auth service instance."""
    return AuthService()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Limit to 5 registrations per minute per IP
async def register(request: Request, register_request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    Register a new user with email, password, and background information.
    """
    try:
        # Check if user already exists
        existing_user = await auth_service.get_user_profile_by_email(register_request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Register the new user
        result = await auth_service.register_user(register_request)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )

        return RegisterResponse(
            user_id=result["user_id"],
            email=result["email"],
            created_at=result["created_at"],
            software_background=result["software_background"],
            hardware_background=result["hardware_background"],
            token=result["token"]
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")  # Limit to 10 login attempts per minute per IP
async def login(request: Request, login_request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    Authenticate user with email and password.
    """
    try:
        result = await auth_service.login_user(login_request)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        return LoginResponse(
            user_id=result["user_id"],
            email=result["email"],
            token=result["token"]
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/logout")
async def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user and invalidate session.
    """
    try:
        token = credentials.credentials
        # In a real implementation, you would invalidate the token
        # For now, we just return a success message
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


# Helper method to get user by email (needed for duplicate check)
# We'll add this to the AuthService class in a moment