"""
API Clients Package

Contains all API integration clients for the Daily Digest.
"""

from .base import BaseAPIClient
from .weather import WeatherClient
from .news import NewsClient
from .stocks import StocksClient
from .quotes import QuotesClient
from .word import WordClient

__all__ = [
    'BaseAPIClient',
    'WeatherClient',
    'NewsClient',
    'StocksClient',
    'QuotesClient',
    'WordClient',
]
