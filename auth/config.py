"""
Better Auth configuration for the interactive book project.

This module sets up Better Auth with custom fields for software and hardware background.
"""

import os
from typing import Optional
from better_fastapi import BetterFastAPI
from better_auth import Auth, EmailPassword


# Get environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "fallback_secret_for_development")
NEXT_PUBLIC_SITE_URL = os.getenv("NEXT_PUBLIC_SITE_URL", "http://localhost:8000")


def get_auth_instance() -> Auth:
    """
    Create and configure the Better Auth instance with custom fields.
    
    The custom fields include:
    - softwareBackground: JSON field for user's software background
    - hardwareBackground: JSON field for user's hardware background
    """
    # Define the auth configuration
    auth_config = Auth(
        secret=BETTER_AUTH_SECRET,
        database_url=DATABASE_URL,
        email_password=EmailPassword(
            enabled=True,
            # Custom fields for user background information
            additional_fields={
                "softwareBackground": {
                    "type": "text",  # Store as JSON string
                    "required": False,
                    "default": "{}"
                },
                "hardwareBackground": {
                    "type": "text",  # Store as JSON string
                    "required": False,
                    "default": "{}"
                }
            }
        ),
        base_url=NEXT_PUBLIC_SITE_URL,
    )
    
    return auth_config


# Create the BetterFastAPI instance with auth
def create_app_with_auth():
    """Create a FastAPI app with Better Auth integrated."""
    auth = get_auth_instance()
    app = BetterFastAPI(auth=auth)
    return app, auth