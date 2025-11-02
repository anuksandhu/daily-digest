"""
Centralized logging configuration for Daily Digest.

Provides structured logging with:
- Configurable log levels
- GitHub Actions-friendly output
- Consistent formatting across all modules
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )
        return super().format(record)


def setup_logger(
    name: str = "daily_digest",
    level: str = "INFO",
    format_type: str = "detailed"
) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: Logger name (typically module name)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 'simple' or 'detailed' formatting
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logger(__name__, level="DEBUG")
        >>> logger.info("Starting application")
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Choose format based on type
    if format_type == "simple":
        fmt = "%(levelname)s: %(message)s"
    else:  # detailed
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Use colored formatter for terminal, plain for CI/CD
    if sys.stdout.isatty():
        formatter = ColoredFormatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
    else:
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def log_api_call(logger: logging.Logger, api_name: str, success: bool, 
                 message: str = "", attempt: Optional[int] = None):
    """
    Structured logging for API calls.
    
    Args:
        logger: Logger instance
        api_name: Name of the API being called
        success: Whether the call succeeded
        message: Additional context
        attempt: Retry attempt number (if applicable)
    """
    status = "SUCCESS" if success else "FAILED"
    attempt_info = f" (attempt {attempt})" if attempt else ""
    
    log_msg = f"[{api_name}] {status}{attempt_info}"
    if message:
        log_msg += f" - {message}"
    
    if success:
        logger.info(log_msg)
    else:
        logger.error(log_msg)