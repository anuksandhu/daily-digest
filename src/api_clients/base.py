"""
Base API Client - Abstract base class for all API integrations.

Provides common functionality:
- Retry logic
- Timeout handling
- Logging
- Error handling patterns

All API clients inherit from this to ensure consistency.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests

from ..utils.logger import setup_logger, log_api_call
from ..utils.retry import retry_api_call


class BaseAPIClient(ABC):
    """
    Abstract base class for all API clients.
    
    Enforces consistent interface and provides common utilities.
    Subclasses must implement fetch() method.
    """
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        """
        Initialize base client.
        
        Args:
            name: Human-readable name for logging (e.g., "Weather API")
            api_key: Optional API key for authenticated endpoints
        """
        self.name = name
        self.api_key = api_key
        self.logger = setup_logger(f"api.{name.lower().replace(' ', '_')}")
        self.session = requests.Session()
        
        # Set default timeout for all requests
        self.default_timeout = 15
    
    @abstractmethod
    def fetch(self) -> Dict[str, Any]:
        """
        Fetch data from the API.
        
        Must be implemented by subclasses.
        
        Returns:
            Dictionary with 'success' bool and 'data' or 'error' keys
            
        Example return format:
            {
                'success': True,
                'data': {...}
            }
            or
            {
                'success': False,
                'error': 'Error message'
            }
        """
        pass
    
    @retry_api_call
    def _make_request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: On network errors (after retries)
        """
        timeout = timeout or self.default_timeout
        
        self.logger.debug(f"Making {method} request to {url}")
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            timeout=timeout
        )
        response.raise_for_status()
        
        return response
    
    def _handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Standardized error handling and logging.
        
        Args:
            error: Exception that occurred
            context: Additional context for error message
            
        Returns:
            Error result dictionary
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        
        log_api_call(
            self.logger,
            self.name,
            success=False,
            message=error_msg
        )
        
        # Return user-friendly error message
        if isinstance(error, requests.Timeout):
            user_msg = f"{self.name} is temporarily unavailable (timeout)."
        elif isinstance(error, requests.ConnectionError):
            user_msg = f"{self.name} is temporarily unavailable (connection error)."
        elif isinstance(error, requests.HTTPError):
            user_msg = f"{self.name} returned an error (status {error.response.status_code})."
        else:
            user_msg = f"{self.name} is temporarily unavailable."
        
        return {
            'success': False,
            'error': user_msg
        }
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()