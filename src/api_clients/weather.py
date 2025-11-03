"""
Weather API Client - OpenWeatherMap integration.

Fetches current weather conditions for a specified location.
"""

from typing import Dict, Any
import requests

from .base import BaseAPIClient


class WeatherClient(BaseAPIClient):
    """
    Client for OpenWeatherMap API.
    
    Provides current weather conditions including:
    - Temperature
    - Weather description
    - Location details
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self, api_key: str, city: str, country: str, units: str = "imperial"):
        """
        Initialize weather client.
        
        Args:
            api_key: OpenWeatherMap API key
            city: City name (e.g., "San Jose")
            country: Country code (e.g., "US")
            units: Temperature units ("imperial" or "metric")
        """
        super().__init__(name="Weather API", api_key=api_key)
        self.city = city
        self.country = country
        self.units = units
        self.location = f"{city},{country}"
    
    def fetch(self) -> Dict[str, Any]:
        """
        Fetch current weather data.
        
        Returns:
            Dictionary with success status and weather data or error message
            
        Example success response:
            {
                'success': True,
                'data': {
                    'temperature': 56.0,
                    'description': 'overcast clouds',
                    'city': 'San Jose',
                    'country': 'US'
                }
            }
        """
        try:
            self.logger.info(f"Fetching weather for {self.location}")
            
            params = {
                'q': self.location,
                'appid': self.api_key,
                'units': self.units
            }
            
            response = self._make_request(self.BASE_URL, params=params)
            data = response.json()
            
            # Extract relevant fields
            weather_data = {
                'temperature': round(data['main']['temp'], 1),
                'description': data['weather'][0]['description'],
                'city': data['name'],
                'country': data['sys']['country']
            }
            
            self.logger.info(
                f"✓ Weather fetched: {weather_data['temperature']}°F, "
                f"{weather_data['description']}"
            )
            
            return {
                'success': True,
                'data': weather_data
            }
        
        except requests.HTTPError as e:
            # Handle specific HTTP errors with user-friendly messages
            if e.response.status_code == 401:
                error_msg = "Weather service: Invalid API key. Please check your credentials."
                self.logger.error(f"Invalid API key: {str(e)}")
                return {
                    'success': False,
                    'error': error_msg
                }
            elif e.response.status_code == 404:
                error_msg = f"Weather service: Location '{self.location}' not found. Please verify city and country."
                self.logger.error(f"Location not found: {self.location}")
                return {
                    'success': False,
                    'error': error_msg
                }
            else:
                # For other HTTP errors, use generic handling
                return self._handle_error(e, "HTTP error")
        
        except (requests.RequestException, KeyError, ValueError) as e:
            return self._handle_error(e, "Failed to fetch weather")
    
    def format_for_display(self, data: Dict[str, Any]) -> str:
        """
        Format weather data for HTML display.
        
        Args:
            data: Weather data dictionary from fetch()
            
        Returns:
            Formatted string for display
        """
        if not data.get('success'):
            return data.get('error', 'Weather data unavailable')
        
        weather = data['data']
        return (
            f"{weather['city']}, {weather['country']}: "
            f"{weather['temperature']}°F with {weather['description']}."
        )