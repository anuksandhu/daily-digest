"""
Tests for Stocks API Client.

Tests stock quote fetching, rate limiting, and error handling.
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.api_clients.stocks import StocksClient


class TestStocksClient:
    """Test suite for StocksClient."""
    
    def test_initialization(self):
        """Test client initializes with correct parameters."""
        client = StocksClient(
            api_key="test_key",
            symbols=["AAPL", "GOOGL"],
            rate_limit_delay=13
        )
        
        assert client.api_key == "test_key"
        assert client.symbols == ["AAPL", "GOOGL"]
        assert client.rate_limit_delay == 13
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_single_symbol_success(self, mock_request, sample_stock_response):
        """Test successful fetch of single stock quote."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = sample_stock_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = StocksClient(api_key="test_key", symbols=["AAPL"], rate_limit_delay=0)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['quotes']) == 1
        assert result['data']['quotes'][0]['symbol'] == 'AAPL'
        assert result['data']['quotes'][0]['price'] == 150.25
        assert result['data']['quotes'][0]['change_percent'] == 1.25
        assert result['data']['quotes'][0]['direction'] == 'up'
    
    @patch('src.api_clients.stocks.time.sleep')
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_multiple_symbols_with_rate_limiting(self, mock_request, mock_sleep, sample_stock_response):
        """Test rate limiting with multiple symbols."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = sample_stock_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = StocksClient(api_key="test_key", symbols=["AAPL", "GOOGL", "MSFT"], rate_limit_delay=13)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['quotes']) == 3
        # Should have called sleep twice (between 2nd and 3rd requests)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(13)
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_rate_limit_error(self, mock_request):
        """Test handling of API rate limit message."""
        # Setup mock to return rate limit message
        mock_response = Mock()
        mock_response.json.return_value = {
            'Note': 'Thank you for using Alpha Vantage! Our standard API rate limit is 5 calls per minute.'
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = StocksClient(api_key="test_key", symbols=["AAPL"], rate_limit_delay=0)
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_invalid_symbol(self, mock_request):
        """Test handling of invalid stock symbol."""
        # Setup mock to return empty quote
        mock_response = Mock()
        mock_response.json.return_value = {'Global Quote': {}}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = StocksClient(api_key="test_key", symbols=["INVALID"], rate_limit_delay=0)
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_partial_success(self, mock_request, sample_stock_response):
        """Test partial success when some symbols fail."""
        # Setup mock to succeed for first call, fail for second
        call_count = [0]
        
        def request_side_effect(*args, **kwargs):
            call_count[0] += 1
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            
            if call_count[0] == 1:
                # First call succeeds
                mock_response.json.return_value = sample_stock_response
            else:
                # Second call fails
                mock_response.json.return_value = {'Global Quote': {}}
            
            return mock_response
        
        mock_request.side_effect = request_side_effect
        
        # Execute
        client = StocksClient(api_key="test_key", symbols=["AAPL", "INVALID"], rate_limit_delay=0)
        result = client.fetch()
        
        # Assert - should still succeed with partial data
        assert result['success'] is True
        assert len(result['data']['quotes']) == 1
        assert len(result['data']['failed']) == 1
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_negative_change(self, mock_request):
        """Test handling of stock with negative price change."""
        # Setup mock with negative change
        mock_response = Mock()
        mock_response.json.return_value = {
            'Global Quote': {
                '05. price': '145.50',
                '10. change percent': '-2.35%'
            }
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = StocksClient(api_key="test_key", symbols=["AAPL"], rate_limit_delay=0)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert result['data']['quotes'][0]['change_percent'] == -2.35
        assert result['data']['quotes'][0]['direction'] == 'down'
    
    def test_format_for_display_success(self):
        """Test formatting of successful stock data."""
        client = StocksClient(api_key="test_key", symbols=["AAPL"], rate_limit_delay=0)
        
        result = {
            'success': True,
            'data': {
                'quotes': [
                    {'symbol': 'AAPL', 'price': 150.25, 'change_percent': 1.25, 'direction': 'up'},
                    {'symbol': 'GOOGL', 'price': 140.50, 'change_percent': -0.75, 'direction': 'down'}
                ],
                'failed': []
            }
        }
        
        formatted = client.format_for_display(result)
        
        assert 'AAPL' in formatted
        assert '$150.25' in formatted
        assert '+1.25%' in formatted
        assert 'GOOGL' in formatted
        assert '$140.50' in formatted
        assert '-0.75%' in formatted
    
    def test_format_for_display_error(self):
        """Test formatting of error response."""
        client = StocksClient(api_key="test_key", symbols=["AAPL"], rate_limit_delay=0)
        
        result = {
            'success': False,
            'error': 'Stock data unavailable'
        }
        
        formatted = client.format_for_display(result)
        
        assert 'unavailable' in formatted.lower()
