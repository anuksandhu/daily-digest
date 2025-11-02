"""
Pytest configuration and shared fixtures.

Provides common test fixtures used across multiple test files.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture
def sample_weather_response():
    """Sample OpenWeatherMap API response."""
    return {
        'main': {'temp': 72.5},
        'weather': [{'description': 'clear sky'}],
        'name': 'San Jose',
        'sys': {'country': 'US'}
    }


@pytest.fixture
def sample_stock_response():
    """Sample Alpha Vantage API response."""
    return {
        'Global Quote': {
            '05. price': '150.25',
            '10. change percent': '+1.25%'
        }
    }


@pytest.fixture
def sample_rss_feed():
    """Sample RSS feed content."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Tech News</title>
        <item>
            <title>New AI Breakthrough</title>
            <link>https://example.com/article1</link>
            <pubDate>Thu, 31 Oct 2025 12:00:00 GMT</pubDate>
        </item>
        <item>
            <title>Quantum Computing Advance</title>
            <link>https://example.com/article2</link>
            <pubDate>Thu, 30 Oct 2025 12:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>'''


@pytest.fixture
def sample_quote_response():
    """Sample ZenQuotes API response."""
    return [
        {
            'q': 'The best way to predict the future is to invent it.',
            'a': 'Alan Kay'
        }
    ]


@pytest.fixture
def sample_word_response():
    """Sample Wordnik API response."""
    return {
        'word': 'serendipity',
        'definitions': [
            {'text': 'The occurrence of events by chance in a happy way.'}
        ]
    }


@pytest.fixture
def mock_config():
    """Mock configuration object."""
    class MockConfig:
        location = {'city': 'San Jose', 'country': 'US'}
        stocks = {'symbols': ['AAPL', 'GOOGL'], 'rate_limit_delay': 0}
        news = {
            'sources': [
                {'name': 'Test Source', 'url': 'https://example.com/rss', 'enabled': True}
            ],
            'max_articles': 5
        }
        quotes = {'source': 'zenquotes'}
        word_of_the_day = {'fallback_enabled': True}
        output = {'filename': 'test_output.html', 'title': 'Test Digest'}
        retry = {'max_attempts': 3, 'initial_delay': 1, 'backoff_multiplier': 2}
        
        def get_api_key(self, service):
            keys = {
                'openweather': 'test_weather_key',
                'alpha_vantage': 'test_stock_key',
                'wordnik': 'test_wordnik_key'
            }
            return keys.get(service)
    
    return MockConfig()


@pytest.fixture
def temp_output_file(tmp_path):
    """Provide a temporary output file path."""
    return tmp_path / "test_output.html"
