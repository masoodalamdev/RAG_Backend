"""
Authentication service layer
Handles business logic for authentication and user profile management
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import logging
import bcrypt
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.models.user_model import User
from src.models.auth import RegisterRequest, LoginRequest
from src.models.user import UserUpdate
from src.database.connection import neon_db
import os
import json


logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "fallback_secret_key_for_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """Service class for authentication and user profile operations."""

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode a JWT access token and return the token data."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return {"id": user_id}
        except JWTError:
            return None
    
    def register_user_sync(self, register_request: RegisterRequest) -> Optional[Dict[str, Any]]:
        """
        Register a new user with email, password, and background information.

        Args:
            register_request: Registration request with user details

        Returns:
            Dictionary with user info and token, or None if registration fails
        """
        db = None
        try:
            logger.info(f"Registering user with email: {register_request.email}")

            # Get database session
            db = neon_db.get_session()

            # Check if user already exists
            existing_user = db.query(User).filter(User.email == register_request.email).first()
            if existing_user:
                logger.warning(f"User with email {register_request.email} already exists")
                return None

            # Hash the password
            hashed_password = self.hash_password(register_request.password)

            # Create new user with custom background fields
            new_user = User(
                email=register_request.email,
                hashed_password=hashed_password,
                software_background=register_request.software_background or {},
                hardware_background=register_request.hardware_background or {}
            )

            # Add user to database
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            # Create JWT token
            token_data = {"sub": str(new_user.id)}
            token = self.create_access_token(data=token_data)

            result = {
                "user_id": str(new_user.id),
                "email": new_user.email,
                "created_at": new_user.created_at,
                "software_background": new_user.software_background or {},
                "hardware_background": new_user.hardware_background or {},
                "token": {
                    "access_token": token,
                    "token_type": "bearer"
                }
            }

            logger.info(f"Successfully registered user with ID: {new_user.id}")
            return result

        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return None
        finally:
            if db:
                db.close()

    async def register_user(self, register_request: RegisterRequest) -> Optional[Dict[str, Any]]:
        """
        Async wrapper for registering a new user.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        # Run the synchronous operation in a thread pool
        return await loop.run_in_executor(None, self.register_user_sync, register_request)
    
    def login_user_sync(self, login_request: LoginRequest) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password.

        Args:
            login_request: Login request with credentials

        Returns:
            Dictionary with user info and token, or None if login fails
        """
        db = None
        try:
            logger.info(f"Logging in user with email: {login_request.email}")

            # Get database session
            db = neon_db.get_session()

            # Find user by email
            user = db.query(User).filter(User.email == login_request.email).first()

            if not user or not self.verify_password(login_request.password, user.hashed_password):
                logger.warning(f"Invalid credentials for email: {login_request.email}")
                return None

            # Create JWT token
            token_data = {"sub": str(user.id)}
            token = self.create_access_token(data=token_data)

            result = {
                "user_id": str(user.id),
                "email": user.email,
                "token": {
                    "access_token": token,
                    "token_type": "bearer"
                }
            }

            logger.info(f"Successfully logged in user with ID: {user.id}")
            return result

        except Exception as e:
            logger.error(f"Error during user login: {str(e)}")
            return None
        finally:
            if db:
                db.close()

    async def login_user(self, login_request: LoginRequest) -> Optional[Dict[str, Any]]:
        """
        Async wrapper for authenticating user with email and password.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        # Run the synchronous operation in a thread pool
        return await loop.run_in_executor(None, self.login_user_sync, login_request)
    
    def get_user_profile_sync(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile information.

        Args:
            user_id: ID of the user whose profile to retrieve

        Returns:
            Dictionary with user profile information, or None if user not found
        """
        db = None
        try:
            logger.info(f"Retrieving profile for user ID: {user_id}")

            # Get database session
            db = neon_db.get_session()

            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.warning(f"User not found with ID: {user_id}")
                return None

            result = {
                "id": str(user.id),
                "email": user.email,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "software_background": user.software_background or {},
                "hardware_background": user.hardware_background or {}
            }

            logger.info(f"Successfully retrieved profile for user ID: {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error retrieving user profile: {str(e)}")
            return None
        finally:
            if db:
                db.close()

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Async wrapper for retrieving user profile information.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        # Run the synchronous operation in a thread pool
        return await loop.run_in_executor(None, self.get_user_profile_sync, user_id)
    
    def update_user_profile_sync(self, user_id: str, profile_update: UserUpdate) -> Optional[Dict[str, Any]]:
        """
        Update user profile information.

        Args:
            user_id: ID of the user whose profile to update
            profile_update: Updated profile information

        Returns:
            Dictionary with updated user profile, or None if update fails
        """
        db = None
        try:
            logger.info(f"Updating profile for user ID: {user_id}")

            # Get database session
            db = neon_db.get_session()

            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                logger.warning(f"User not found with ID: {user_id}")
                return None

            # Update user fields if provided
            if profile_update.software_background is not None:
                user.software_background = profile_update.software_background
            if profile_update.hardware_background is not None:
                user.hardware_background = profile_update.hardware_background

            # Commit changes to database
            db.commit()
            db.refresh(user)

            # Return updated profile
            result = {
                "id": str(user.id),
                "email": user.email,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "software_background": user.software_background or {},
                "hardware_background": user.hardware_background or {}
            }

            logger.info(f"Successfully updated profile for user ID: {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return None
        finally:
            if db:
                db.close()

    async def update_user_profile(self, user_id: str, profile_update: UserUpdate) -> Optional[Dict[str, Any]]:
        """
        Async wrapper for updating user profile information.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        # Run the synchronous operation in a thread pool
        return await loop.run_in_executor(None, self.update_user_profile_sync, user_id, profile_update)
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify authentication token.

        Args:
            token: Authentication token to verify

        Returns:
            User data if token is valid, None otherwise
        """
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]

            # Decode the JWT token
            user_data = self.decode_access_token(token)
            return user_data
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None

    def get_user_profile_by_email_sync(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile by email.

        Args:
            email: Email of the user to retrieve

        Returns:
            Dictionary with user profile information, or None if user not found
        """
        db = None
        try:
            logger.info(f"Retrieving profile for user with email: {email}")

            # Get database session
            db = neon_db.get_session()

            # Get user from database by email
            user = db.query(User).filter(User.email == email).first()

            if not user:
                logger.warning(f"User not found with email: {email}")
                return None

            result = {
                "id": str(user.id),
                "email": user.email,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "software_background": user.software_background or {},
                "hardware_background": user.hardware_background or {}
            }

            logger.info(f"Successfully retrieved profile for user with email: {email}")
            return result

        except Exception as e:
            logger.error(f"Error retrieving user profile by email: {str(e)}")
            return None
        finally:
            if db:
                db.close()

    async def get_user_profile_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Async wrapper for retrieving user profile by email.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        # Run the synchronous operation in a thread pool
        return await loop.run_in_executor(None, self.get_user_profile_by_email_sync, email)