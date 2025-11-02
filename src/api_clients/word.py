"""
Word of the Day API Client - Wordnik with fallback.

Fetches word of the day from:
1. Wordnik (primary, requires API key)
2. Free Dictionary API (fallback, no key needed)

Demonstrates graceful degradation.
"""

from typing import Dict, Any, Optional
import requests
from datetime import datetime
import random

from .base import BaseAPIClient


class WordClient(BaseAPIClient):
    """
    Client for Word of the Day.
    
    Uses Wordnik API as primary source (requires key).
    Falls back to Dictionary API if Wordnik unavailable.
    """
    
    WORDNIK_URL = "https://api.wordnik.com/v4/words.json/wordOfTheDay"
    DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"
    
    # Fallback word list for complete failure
    FALLBACK_WORDS = [
        "serendipity", "ephemeral", "luminous", "resilient", "paradigm",
        "eloquent", "pragmatic", "ubiquitous", "catalyst", "synergy"
    ]
    
    def __init__(self, api_key: Optional[str] = None, fallback_enabled: bool = True):
        """
        Initialize word client.
        
        Args:
            api_key: Wordnik API key (optional)
            fallback_enabled: Whether to use fallback sources
        """
        super().__init__(name="Word API", api_key=api_key)
        self.fallback_enabled = fallback_enabled
    
    def fetch(self) -> Dict[str, Any]:
        """
        Fetch word of the day.
        
        Returns:
            Dictionary with success status and word data
            
        Example success response:
            {
                'success': True,
                'data': {
                    'word': 'ephemeral',
                    'definition': 'Lasting for a very short time',
                    'source': 'wordnik' or 'dictionary_api' or 'fallback'
                }
            }
        """
        # Try Wordnik first if API key provided
        if self.api_key:
            result = self._fetch_from_wordnik()
            if result['success']:
                return result
            
            self.logger.warning("Wordnik failed, trying fallback")
        else:
            self.logger.info("No Wordnik API key, using fallback")
        
        # Try fallback if enabled
        if self.fallback_enabled:
            return self._fetch_fallback()
        
        return {
            'success': False,
            'error': 'Word of the day is unavailable.'
        }
    
    def _fetch_from_wordnik(self) -> Dict[str, Any]:
        """
        Fetch from Wordnik API.
        
        Returns:
            Word data dictionary
        """
        try:
            self.logger.info("Fetching word from Wordnik")
            
            params = {'api_key': self.api_key}
            response = self._make_request(self.WORDNIK_URL, params=params)
            data = response.json()
            
            # Extract word and first definition
            word = data['word']
            definitions = data.get('definitions', [])
            definition = definitions[0]['text'] if definitions else "No definition available"
            
            self.logger.info(f"✓ Word fetched from Wordnik: {word}")
            
            return {
                'success': True,
                'data': {
                    'word': word,
                    'definition': definition,
                    'source': 'wordnik'
                }
            }
        
        except (requests.RequestException, KeyError, IndexError) as e:
            self.logger.warning(f"Wordnik fetch failed: {str(e)}")
            return {'success': False}
    
    def _fetch_fallback(self) -> Dict[str, Any]:
        """
        Fetch from fallback Dictionary API.
        
        Uses a predefined word list and fetches definition from free API.
        
        Returns:
            Word data dictionary
        """
        try:
            # Pick a word based on day of year (consistent daily)
            day_of_year = datetime.now().timetuple().tm_yday
            word = self.FALLBACK_WORDS[day_of_year % len(self.FALLBACK_WORDS)]
            
            self.logger.info(f"Fetching definition for fallback word: {word}")
            
            url = f"{self.DICTIONARY_URL}/{word}"
            response = self._make_request(url)
            data = response.json()
            
            # Extract first definition
            meanings = data[0]['meanings'][0]
            definition = meanings['definitions'][0]['definition']
            
            self.logger.info(f"✓ Word fetched from fallback: {word}")
            
            return {
                'success': True,
                'data': {
                    'word': word,
                    'definition': definition.capitalize(),
                    'source': 'dictionary_api'
                }
            }
        
        except (requests.RequestException, KeyError, IndexError) as e:
            self.logger.error(f"All word sources failed: {str(e)}")
            
            # Last resort: random word with generic message
            word = random.choice(self.FALLBACK_WORDS)
            return {
                'success': True,
                'data': {
                    'word': word,
                    'definition': 'A wonderful word worth exploring!',
                    'source': 'fallback'
                }
            }
    
    def format_for_display(self, data: Dict[str, Any]) -> str:
        """
        Format word for HTML display.
        
        Args:
            data: Word data dictionary from fetch()
            
        Returns:
            Formatted HTML string
        """
        if not data.get('success'):
            return data.get('error', 'Word of the day unavailable')
        
        word_data = data['data']
        return (
            f"<strong>{word_data['word'].title()}</strong>: "
            f"{word_data['definition']}"
        )