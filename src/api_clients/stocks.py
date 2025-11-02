"""
Stocks API Client - Alpha Vantage integration.

Fetches real-time stock quotes with proper rate limiting.
Alpha Vantage free tier: 5 requests/minute, 500/day
"""

from typing import Dict, Any, List
import time
import requests

from .base import BaseAPIClient


class StocksClient(BaseAPIClient):
    """
    Client for Alpha Vantage stock API.
    
    Fetches real-time stock quotes with:
    - Current price
    - Change percentage
    - Automatic rate limiting
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str, symbols: List[str], rate_limit_delay: int = 13):
        """
        Initialize stocks client.
        
        Args:
            api_key: Alpha Vantage API key
            symbols: List of stock symbols (e.g., ["AAPL", "GOOGL"])
            rate_limit_delay: Seconds to wait between requests (default 13 for 5/min limit)
        """
        super().__init__(name="Stocks API", api_key=api_key)
        self.symbols = symbols
        self.rate_limit_delay = rate_limit_delay
    
    def fetch(self) -> Dict[str, Any]:
        """
        Fetch stock quotes for all symbols.
        
        Returns:
            Dictionary with success status and stock data
            
        Example success response:
            {
                'success': True,
                'data': {
                    'quotes': [
                        {
                            'symbol': 'AAPL',
                            'price': 271.40,
                            'change_percent': 0.63,
                            'direction': 'up'
                        },
                        ...
                    ]
                }
            }
        """
        quotes = []
        failed_symbols = []
        
        for i, symbol in enumerate(self.symbols):
            # Rate limiting: pause before subsequent requests
            if i > 0:
                self.logger.debug(f"Rate limit: waiting {self.rate_limit_delay}s")
                time.sleep(self.rate_limit_delay)
            
            try:
                quote = self._fetch_quote(symbol)
                if quote:
                    quotes.append(quote)
                else:
                    failed_symbols.append(symbol)
                    
            except Exception as e:
                self.logger.warning(f"Failed to fetch {symbol}: {str(e)}")
                failed_symbols.append(symbol)
        
        # Determine overall success
        if not quotes and failed_symbols:
            return {
                'success': False,
                'error': 'Stock market data is temporarily unavailable.'
            }
        
        self.logger.info(
            f"✓ Fetched {len(quotes)} stock quotes "
            f"({len(failed_symbols)} failed)"
        )
        
        return {
            'success': True,
            'data': {
                'quotes': quotes,
                'failed': failed_symbols
            }
        }
    
    def _fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch quote for a single symbol.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            
        Returns:
            Quote dictionary or None if failed
        """
        self.logger.debug(f"Fetching quote for {symbol}")
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = self._make_request(self.BASE_URL, params=params)
        data = response.json()
        
        # Check for rate limit message in response
        if "Note" in data:
            raise ValueError("API rate limit reached")
        
        # Check for valid quote data
        quote_data = data.get('Global Quote')
        if not quote_data:
            raise ValueError(f"No data returned for {symbol}")
        
        # Parse and format quote
        price = float(quote_data['05. price'])
        change_percent_str = quote_data['10. change percent'].rstrip('%')
        change_percent = float(change_percent_str)
        
        return {
            'symbol': symbol,
            'price': round(price, 2),
            'change_percent': round(change_percent, 2),
            'direction': 'up' if change_percent >= 0 else 'down'
        }
    
    def format_for_display(self, data: Dict[str, Any]) -> str:
        """
        Format stock quotes for HTML display.
        
        Args:
            data: Stock data dictionary from fetch()
            
        Returns:
            Formatted string for display
        """
        if not data.get('success'):
            return data.get('error', 'Stock data unavailable')
        
        quotes = data['data']['quotes']
        
        if not quotes:
            return "No stock data available."
        
        # Format each quote with arrow indicator
        lines = []
        for quote in quotes:
            arrow = "▲" if quote['direction'] == 'up' else "▼"
            color = "green" if quote['direction'] == 'up' else "red"
            
            lines.append(
                f"{quote['symbol']}: ${quote['price']:.2f} "
                f"(<span style='color: {color};'>{quote['change_percent']:+.2f}%</span>) "
                f"{arrow}"
            )
        
        return "<br>".join(lines)