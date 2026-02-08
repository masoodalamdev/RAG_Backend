"""
Rate limiting utilities for authentication endpoints
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def add_rate_limiting(app: FastAPI):
    """
    Add rate limiting to the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Add the rate limit exceeded handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)