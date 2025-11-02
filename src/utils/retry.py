"""
Retry logic with exponential backoff for API calls.

Uses the tenacity library for production-grade retry behavior:
- Exponential backoff (1s, 2s, 4s, etc.)
- Configurable max attempts
- Logs retry attempts
- Handles specific exception types
"""

from functools import wraps
from typing import Callable, Type, Tuple
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import logging

from .logger import setup_logger

logger = setup_logger(__name__)


def create_retry_decorator(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    exceptions: Tuple[Type[Exception], ...] = (requests.RequestException,)
):
    """
    Factory function to create a retry decorator with custom parameters.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds (initial delay)
        max_wait: Maximum wait time in seconds
        exceptions: Tuple of exception types to retry on
        
    Returns:
        Configured retry decorator
        
    Example:
        >>> retry_api_call = create_retry_decorator(max_attempts=3)
        >>> @retry_api_call
        ... def fetch_data():
        ...     return requests.get(url)
    """
    return retry(
        # Stop after N attempts
        stop=stop_after_attempt(max_attempts),
        
        # Exponential backoff: 2^n * min_wait (capped at max_wait)
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        
        # Only retry on specific exceptions
        retry=retry_if_exception_type(exceptions),
        
        # Log before sleeping (retry attempt)
        before_sleep=before_sleep_log(logger, logging.WARNING),
        
        # Log after all attempts
        after=after_log(logger, logging.INFO),
        
        # Re-raise the exception if all attempts fail
        reraise=True
    )


# Default retry decorator with standard settings
retry_api_call = create_retry_decorator(
    max_attempts=3,
    min_wait=1,
    max_wait=10,
    exceptions=(
        requests.RequestException,
        requests.Timeout,
        requests.ConnectionError
    )
)


def with_timeout(timeout: int = 15):
    """
    Decorator to add timeout to functions making HTTP requests.
    
    Args:
        timeout: Timeout in seconds
        
    Example:
        >>> @with_timeout(10)
        ... def fetch_data(url):
        ...     return requests.get(url)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add timeout to kwargs if not present
            if 'timeout' not in kwargs:
                kwargs['timeout'] = timeout
            return func(*args, **kwargs)
        return wrapper
    return decorator