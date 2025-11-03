"""
Tests for Weather API Client.

Tests match actual WeatherClient API signature.
Updated with robust error message checking using keywords.
"""

import pytest
from unittest.mock import Mock, patch
import requests
from src.api_clients.weather import WeatherClient


class TestWeatherClient:
    """Test suite for WeatherClient."""
    
    def test_initialization(self):
        """Test client initializes with API key, city, and country."""
        client = WeatherClient(api_key="test_key", city="San Francisco", country="US")
        
        assert client.api_key == "test_key"
        assert client.city == "San Francisco"
        assert client.country == "US"
        assert client.location == "San Francisco,US"
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_success(self, mock_request):
        """Test successful weather data fetch."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'main': {
                'temp': 72.5,
                'feels_like': 70.0,
                'humidity': 65
            },
            'weather': [
                {'description': 'partly cloudy', 'icon': '02d'}
            ],
            'name': 'San Francisco',
            'sys': {'country': 'US'}
        }
        mock_request.return_value = mock_response
        
        # Execute
        client = WeatherClient(api_key="test_key", city="San Francisco", country="US")
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert result['data']['temperature'] == 72.5
        assert result['data']['description'] == 'partly cloudy'
        assert result['data']['city'] == 'San Francisco'
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_api_error_401(self, mock_request):
        """Test handling of 401 authentication error.
        
        Uses robust keyword checking that tolerates text variations.
        """
        # Setup mock to raise 401 error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_request.return_value = mock_response
        
        # Execute
        client = WeatherClient(api_key="bad_key", city="San Francisco", country="US")
        result = client.fetch()
        
        # Assert - use flexible keyword matching
        assert result['success'] is False
        assert 'error' in result
        
        error_lower = result['error'].lower()
        # Check for keywords that indicate an API key issue
        assert any(keyword in error_lower for keyword in ['api key', 'invalid', 'credentials', 'authentication'])
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_location_not_found_404(self, mock_request):
        """Test handling of 404 location not found error.
        
        Uses robust keyword checking that tolerates text variations.
        """
        # Setup mock to raise 404 error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_request.return_value = mock_response
        
        # Execute
        client = WeatherClient(api_key="test_key", city="InvalidCity", country="XX")
        result = client.fetch()
        
        # Assert - use flexible keyword matching
        assert result['success'] is False
        assert 'error' in result
        
        error_lower = result['error'].lower()
        # Check for keywords that indicate a location issue
        assert any(keyword in error_lower for keyword in ['not found', 'location', 'city', 'invalid'])
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_timeout(self, mock_request):
        """Test handling of request timeout."""
        # Setup mock to raise timeout
        mock_request.side_effect = requests.Timeout("Connection timeout")
        
        # Execute
        client = WeatherClient(api_key="test_key", city="San Francisco", country="US")
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
        assert 'timeout' in result['error'].lower() or 'unavailable' in result['error'].lower()
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_connection_error(self, mock_request):
        """Test handling of connection error."""
        # Setup mock to raise connection error
        mock_request.side_effect = requests.ConnectionError("Network error")
        
        # Execute
        client = WeatherClient(api_key="test_key", city="San Francisco", country="US")
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    def test_format_for_display_success(self):
        """Test formatting of successful weather data."""
        client = WeatherClient(api_key="test_key", city="San Francisco", country="US")
        
        result = {
            'success': True,
            'data': {
                'city': 'San Francisco',
                'country': 'US',
                'temperature': 72.5,
                'description': 'partly cloudy'
            }
        }
        
        formatted = client.format_for_display(result)
        
        assert 'San Francisco' in formatted
        assert 'US' in formatted
        assert '72.5' in formatted
        assert 'partly cloudy' in formatted
    
    def test_format_for_display_error(self):
        """Test formatting of error response."""
        client = WeatherClient(api_key="test_key", city="San Francisco", country="US")
        
        result = {
            'success': False,
            'error': 'Weather data unavailable'
        }
        
        formatted = client.format_for_display(result)
        
        assert 'unavailable' in formatted.lower()
    
    def test_client_uses_correct_endpoint(self):
        """Test that client uses the correct API endpoint."""
        client = WeatherClient(api_key="test_key", city="San Francisco", country="US")
        
        # Verify the base URL is set correctly
        assert 'openweathermap.org' in client.BASE_URL
        assert 'weather' in client.BASE_URL