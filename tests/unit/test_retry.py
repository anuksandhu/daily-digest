"""
Tests for Retry Utility.

Tests exponential backoff retry logic.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from src.utils.retry import retry_api_call, create_retry_decorator


class TestRetryLogic:
    """Test suite for retry functionality."""
    
    def test_retry_success_on_first_attempt(self):
        """Test that successful calls don't trigger retries."""
        # Create a mock function that succeeds
        mock_func = Mock(return_value="success")
        decorated_func = retry_api_call(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test retry succeeds after initial failures."""
        # Create mock that fails twice then succeeds
        mock_func = Mock(side_effect=[
            requests.Timeout("timeout"),
            requests.ConnectionError("connection error"),
            "success"
        ])
        decorated_func = retry_api_call(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_exhausts_attempts(self):
        """Test that retry stops after max attempts."""
        # Create mock that always fails
        mock_func = Mock(side_effect=requests.Timeout("always fails"))
        decorated_func = retry_api_call(mock_func)
        
        with pytest.raises(requests.Timeout):
            decorated_func()
        
        # Default is 3 attempts
        assert mock_func.call_count == 3
    
    def test_retry_only_on_specific_exceptions(self):
        """Test that retry only happens for network errors."""
        # Create mock that raises non-retryable exception
        mock_func = Mock(side_effect=ValueError("not a network error"))
        decorated_func = retry_api_call(mock_func)
        
        with pytest.raises(ValueError):
            decorated_func()
        
        # Should not retry for ValueError
        assert mock_func.call_count == 1
    
    def test_custom_retry_decorator(self):
        """Test creating custom retry decorator with different settings."""
        # Create decorator with 2 max attempts
        custom_retry = create_retry_decorator(
            max_attempts=2,
            min_wait=0,
            max_wait=1,
            exceptions=(requests.RequestException,)
        )
        
        mock_func = Mock(side_effect=requests.Timeout("fails"))
        decorated_func = custom_retry(mock_func)
        
        with pytest.raises(requests.Timeout):
            decorated_func()
        
        assert mock_func.call_count == 2
    
    def test_retry_logs_attempts(self):
        """Test that retry attempts occur (verified via call count)."""
        # Setup mock that fails once then succeeds
        mock_func = Mock(side_effect=[
            requests.Timeout("fail"),
            "success"
        ])
        decorated_func = retry_api_call(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        # Verify retry happened by checking function was called twice
        assert mock_func.call_count == 2
    
    def test_retry_preserves_function_signature(self):
        """Test that decorator preserves original function signature."""
        @retry_api_call
        def sample_func(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"
        
        result = sample_func("a", "b", kwarg1="c")
        
        assert result == "a-b-c"
        assert sample_func.__name__ == "sample_func"
