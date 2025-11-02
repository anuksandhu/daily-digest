"""
Tests for Weather API Client.

Tests weather data fetching, error handling, and display formatting.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from src.api_clients.weather import WeatherClient


class TestWeatherClient:
    """Test suite for WeatherClient."""
    
    def test_initialization(self):
        """Test client initializes with correct parameters."""
        client = WeatherClient(
            api_key="test_key",
            city="San Jose",
            country="US"
        )
        
        assert client.api_key == "test_key"
        assert client.city == "San Jose"
        assert client.country == "US"
        assert client.location == "San Jose,US"
        assert client.units == "imperial"  # default
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_success(self, mock_request, sample_weather_response):
        """Test successful weather data fetch."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = sample_weather_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = WeatherClient(api_key="test_key", city="San Jose", country="US")
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert 'data' in result
        assert result['data']['temperature'] == 72.5
        assert result['data']['description'] == 'clear sky'
        assert result['data']['city'] == 'San Jose'
        assert result['data']['country'] == 'US'
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_api_error_401(self, mock_request):
        """Test handling of invalid API key (401 error)."""
        # Setup mock to raise 401 error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_request.return_value = mock_response
        
        # Execute
        client = WeatherClient(api_key="invalid_key", city="San Jose", country="US")
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
        assert 'Invalid API key' in result['error'] or 'temporarily unavailable' in result['error']
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_location_not_found_404(self, mock_request):
        """Test handling of invalid location (404 error)."""
        # Setup mock to raise 404 error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_request.return_value = mock_response
        
        # Execute
        client = WeatherClient(api_key="test_key", city="InvalidCity", country="XX")
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_timeout(self, mock_request):
        """Test handling of request timeout."""
        # Setup mock to raise timeout
        mock_request.side_effect = requests.Timeout("Connection timeout")
        
        # Execute
        client = WeatherClient(api_key="test_key", city="San Jose", country="US")
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
        assert 'timeout' in result['error'].lower() or 'unavailable' in result['error'].lower()
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_connection_error(self, mock_request):
        """Test handling of network connection error."""
        # Setup mock to raise connection error
        mock_request.side_effect = requests.ConnectionError("Network unreachable")
        
        # Execute
        client = WeatherClient(api_key="test_key", city="San Jose", country="US")
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    def test_format_for_display_success(self, sample_weather_response):
        """Test formatting of successful weather data."""
        client = WeatherClient(api_key="test_key", city="San Jose", country="US")
        
        result = {
            'success': True,
            'data': {
                'temperature': 72.5,
                'description': 'clear sky',
                'city': 'San Jose',
                'country': 'US'
            }
        }
        
        formatted = client.format_for_display(result)
        
        assert 'San Jose' in formatted
        assert 'US' in formatted
        assert '72.5' in formatted or '72' in formatted
        assert 'clear sky' in formatted
    
    def test_format_for_display_error(self):
        """Test formatting of error response."""
        client = WeatherClient(api_key="test_key", city="San Jose", country="US")
        
        result = {
            'success': False,
            'error': 'Weather service unavailable'
        }
        
        formatted = client.format_for_display(result)
        
        assert 'unavailable' in formatted.lower() or 'error' in formatted.lower()
    
    def test_client_uses_correct_endpoint(self):
        """Test that client uses correct API endpoint."""
        client = WeatherClient(api_key="test_key", city="San Jose", country="US")
        
        assert "openweathermap.org" in client.BASE_URL
        assert "weather" in client.BASE_URL
