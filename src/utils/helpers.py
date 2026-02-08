import os
import logging
from typing import Optional
from fastapi import HTTPException, status
from functools import wraps
import traceback
import time
from datetime import datetime


def setup_logging(name: str, log_file: Optional[str] = None, level: int = logging.INFO):
    """
    Function to setup logging with the specified name and level.
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_exception(logger: logging.Logger):
    """
    Decorator to log exceptions with traceback.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {str(e)}")
                logger.error(traceback.format_exc())
                raise
        return wrapper
    return decorator


def timing_logger(logger: logging.Logger):
    """
    Decorator to log execution time of functions.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        return wrapper
    return decorator


def create_error_response(error_message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
    """
    Creates a standardized error response.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "error": error_message,
        "status_code": status_code
    }


def handle_http_error(status_code: int, detail: str):
    """
    Raises an HTTPException with the given status code and detail.
    """
    raise HTTPException(status_code=status_code, detail=detail)


# Pre-configured loggers
app_logger = setup_logging("rag_chatbot_app", "logs/app.log")
api_logger = setup_logging("rag_chatbot_api", "logs/api.log")
rag_logger = setup_logging("rag_chatbot_rag", "logs/rag.log")