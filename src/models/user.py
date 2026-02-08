"""
User model with custom background fields
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class SoftwareBackground(BaseModel):
    """Software background information for user profiles."""
    languages: List[str] = []
    frameworks: List[str] = []
    experience_years: int = 0

    @field_validator('experience_years')
    def validate_experience_years(cls, v):
        if v < 0 or v > 50:
            raise ValueError('Experience years must be between 0 and 50')
        return v

    @field_validator('languages')
    def validate_languages(cls, v):
        # Could add validation for valid programming languages
        return v

    @field_validator('frameworks')
    def validate_frameworks(cls, v):
        # Could add validation for valid frameworks
        return v


class HardwareBackground(BaseModel):
    """Hardware background information for user profiles."""
    devices: List[str] = []
    os_preference: str = ""
    setup_description: str = ""

    @field_validator('os_preference')
    def validate_os_preference(cls, v):
        valid_os = ['Windows', 'macOS', 'Linux']
        if v and v not in valid_os:
            raise ValueError(f'OS preference must be one of {valid_os}')
        return v

    @field_validator('setup_description')
    def validate_setup_description(cls, v):
        if len(v) > 500:
            raise ValueError('Setup description must be 500 characters or less')
        return v


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    email_verified: bool = False


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str
    software_background: Optional[SoftwareBackground] = None
    hardware_background: Optional[HardwareBackground] = None

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


class UserUpdate(BaseModel):
    """Model for updating user profile."""
    software_background: Optional[SoftwareBackground] = None
    hardware_background: Optional[HardwareBackground] = None


class User(UserBase):
    """Complete user model with all fields."""
    id: str
    software_background: Optional[Dict[str, Any]] = {}
    hardware_background: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True