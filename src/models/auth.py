"""
Authentication-related models
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """Authentication token model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data model."""
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Request model for login."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Request model for registration."""
    email: EmailStr
    password: str
    software_background: Optional[dict] = None
    hardware_background: Optional[dict] = None

    @field_validator('password')
    def validate_password(cls, v):
        # Password validation: min 8 chars, with uppercase, lowercase, number, and special char
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError('Password must contain uppercase, lowercase, number, and special character')
        
        return v

    @field_validator('email')
    def validate_email_format(cls, v):
        # Email validation is handled by EmailStr, but we can add additional checks if needed
        return v


class RegisterResponse(BaseModel):
    """Response model for registration."""
    user_id: str
    email: EmailStr
    created_at: datetime
    software_background: Optional[dict] = {}
    hardware_background: Optional[dict] = {}
    token: Token  # Changed from str to Token to match the returned data structure


class LoginResponse(BaseModel):
    """Response model for login."""
    user_id: str
    email: EmailStr
    token: Token


class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    id: str
    email: EmailStr
    created_at: datetime
    updated_at: Optional[datetime] = None  # Updated at can be None initially
    software_background: Optional[dict] = {}
    hardware_background: Optional[dict] = {}