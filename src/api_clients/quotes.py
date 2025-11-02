"""
Quotes API Client - ZenQuotes integration.

Fetches inspirational quote of the day.
Free service, no API key required!
"""

from typing import Dict, Any
import requests

from .base import BaseAPIClient


class QuotesClient(BaseAPIClient):
    """
    Client for ZenQuotes API.
    
    Fetches daily inspirational quote with author.
    No API key required - completely free service.
    """
    
    # ZenQuotes provides "quote of the day" endpoint
    QUOTE_URL = "https://zenquotes.io/api/today"
    
    def __init__(self):
        """Initialize quotes client (no API key needed)."""
        super().__init__(name="Quotes API")
    
    def fetch(self) -> Dict[str, Any]:
        """
        Fetch quote of the day.
        
        Returns:
            Dictionary with success status and quote data
            
        Example success response:
            {
                'success': True,
                'data': {
                    'text': 'The best way to predict the future is to invent it.',
                    'author': 'Alan Kay'
                }
            }
        """
        try:
            self.logger.info("Fetching quote of the day")
            
            response = self._make_request(self.QUOTE_URL)
            data = response.json()
            
            # ZenQuotes returns a list with one quote
            if not data or not isinstance(data, list):
                raise ValueError("Unexpected response format")
            
            quote_data = data[0]
            
            result = {
                'text': quote_data['q'],
                'author': quote_data['a']
            }
            
            self.logger.info(f"✓ Quote fetched: \"{result['text'][:50]}...\"")
            
            return {
                'success': True,
                'data': result
            }
        
        except (requests.RequestException, KeyError, ValueError, IndexError) as e:
            return self._handle_error(e, "Failed to fetch quote")
    
    def format_for_display(self, data: Dict[str, Any]) -> str:
        """
        Format quote for HTML display.
        
        Args:
            data: Quote data dictionary from fetch()
            
        Returns:
            Formatted HTML string
        """
        if not data.get('success'):
            return data.get('error', 'Quote of the day unavailable')
        
        quote = data['data']
        return f'"{quote["text"]}" — <em>{quote["author"]}</em>'