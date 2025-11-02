"""
Utilities Package

Common utilities for logging, retry logic, and HTML generation.
"""

from .logger import setup_logger, log_api_call
from .retry import retry_api_call, create_retry_decorator
from .html_builder import build_digest_html, build_error_html

__all__ = [
    'setup_logger',
    'log_api_call',
    'retry_api_call',
    'create_retry_decorator',
    'build_digest_html',
    'build_error_html',
]
