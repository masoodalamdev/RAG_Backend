"""
Authentication module for the interactive book project.

This module implements authentication functionality with custom fields for 
software and hardware background information using FastAPI, SQLAlchemy, and JWT.
"""

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
from pydantic import BaseModel, Field
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Text
from ..database.connection import neon_db
from ..models.user_model import User


# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize security scheme
security = HTTPBearer()


class SoftwareBackground(BaseModel):
    """Software background information for a user."""
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    experience_years: int = 0


class HardwareBackground(BaseModel):
    """Hardware background information for a user."""
    devices: list[str] = Field(default_factory=list)
    os_preference: list[str] = Field(default_factory=list)
    setup_description: str = ""


class UserCreateRequest(BaseModel):
    """Request model for creating a new user."""
    email: str
    password: str
    first_name: str
    last_name: str
    software_background: Optional[SoftwareBackground] = None
    hardware_background: Optional[HardwareBackground] = None


class UserUpdateRequest(BaseModel):
    """Request model for updating user information."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    software_background: Optional[SoftwareBackground] = None
    hardware_background: Optional[HardwareBackground] = None


class UserResponse(BaseModel):
    """Response model for user information."""
    id: str
    email: str
    first_name: str
    last_name: str
    software_background: Optional[Dict[str, Any]]
    hardware_background: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""
    email: Optional[str] = None


def get_db():
    """Dependency to get database session."""
    db = neon_db.get_session()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode a JWT access token and return the token data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
        return token_data
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get the current user based on the JWT token."""
    token = credentials.credentials
    token_data = decode_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user