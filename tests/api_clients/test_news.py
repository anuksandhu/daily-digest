"""
Tests for News API Client (RSS feeds).

FIXES:
- Using real date tuples for published_parsed instead of Mock objects
- This allows proper sorting without comparison errors
- Date tuples follow the format: (year, month, day, hour, minute, second, weekday, yearday, isdst)
"""

import pytest
from unittest.mock import Mock, patch
from src.api_clients.news import NewsClient


class TestNewsClient:
    """Test suite for NewsClient."""
    
    def test_initialization(self):
        """Test client initializes with sources."""
        sources = [
            {'name': 'TechCrunch', 'url': 'https://techcrunch.com/feed/', 'enabled': True},
            {'name': 'Disabled Source', 'url': 'https://example.com/feed/', 'enabled': False}
        ]
        
        client = NewsClient(sources=sources, max_articles=5)
        
        # Should only include enabled sources
        assert len(client.sources) == 1
        assert client.sources[0]['name'] == 'TechCrunch'
        assert client.max_articles == 5
    
    @patch('src.api_clients.news.feedparser.parse')
    def test_fetch_success_single_source(self, mock_parse):
        """Test successful fetch from a single RSS source.
        
        FIX: Use real date tuples instead of Mock objects for published_parsed.
        """
        # Setup mock with REAL date tuples
        mock_feed = Mock()
        mock_feed.bozo = False
        mock_feed.entries = [
            Mock(
                title='Article 1',
                link='https://example.com/1',
                published_parsed=(2025, 10, 31, 12, 0, 0, 3, 304, 0)  # Most recent
            ),
            Mock(
                title='Article 2',
                link='https://example.com/2',
                published_parsed=(2025, 10, 30, 12, 0, 0, 2, 303, 0)  # Older
            )
        ]
        # Configure Mock.get() to return the actual value
        for entry in mock_feed.entries:
            entry.get = lambda key, default=None, entry=entry: getattr(entry, key, default)
        
        mock_parse.return_value = mock_feed
        
        # Execute
        sources = [{'name': 'Test Source', 'url': 'https://example.com/feed/', 'enabled': True}]
        client = NewsClient(sources=sources, max_articles=5)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert 'articles' in result['data']
        assert len(result['data']['articles']) == 2
        assert result['data']['articles'][0]['title'] == 'Article 1'
        assert result['data']['source_count'] == 1
    
    @patch('src.api_clients.news.feedparser.parse')
    def test_fetch_multiple_sources(self, mock_parse):
        """Test aggregation from multiple RSS sources.
        
        FIX: Use real date tuples for proper sorting across sources.
        """
        def parse_side_effect(url):
            feed = Mock()
            feed.bozo = False
            if 'source1' in url:
                entry = Mock(
                    title='Source1 Article',
                    link='https://s1.com/1',
                    published_parsed=(2025, 10, 31, 12, 0, 0, 3, 304, 0)  # Most recent
                )
                entry.get = lambda key, default=None, e=entry: getattr(e, key, default)
                feed.entries = [entry]
            else:
                entry = Mock(
                    title='Source2 Article',
                    link='https://s2.com/1',
                    published_parsed=(2025, 10, 31, 10, 0, 0, 3, 304, 0)  # Slightly older
                )
                entry.get = lambda key, default=None, e=entry: getattr(e, key, default)
                feed.entries = [entry]
            return feed
        
        mock_parse.side_effect = parse_side_effect
        
        # Execute
        sources = [
            {'name': 'Source1', 'url': 'https://source1.com/feed/', 'enabled': True},
            {'name': 'Source2', 'url': 'https://source2.com/feed/', 'enabled': True}
        ]
        client = NewsClient(sources=sources, max_articles=5)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['articles']) == 2
        assert result['data']['source_count'] == 2
        # Should be sorted by date (most recent first)
        assert result['data']['articles'][0]['title'] == 'Source1 Article'
    
    @patch('src.api_clients.news.feedparser.parse')
    def test_fetch_max_articles_limit(self, mock_parse):
        """Test that max_articles limit is respected.
        
        FIX: Use real date tuples with descending dates for proper sorting.
        """
        # Setup mock with 10 articles, but we'll only keep 3
        mock_feed = Mock()
        mock_feed.bozo = False
        
        # Create entries with descending dates (newer to older)
        entries = []
        for i in range(10):
            entry = Mock(
                title=f'Article {i}',
                link=f'https://example.com/{i}',
                # Create descending dates (Oct 31 down to Oct 22)
                published_parsed=(2025, 10, 31-i, 12, 0, 0, 3, 304-i, 0)
            )
            entry.get = lambda key, default=None, e=entry: getattr(e, key, default)
            entries.append(entry)
        
        mock_feed.entries = entries
        mock_parse.return_value = mock_feed
        
        # Execute with max_articles=3
        sources = [{'name': 'Test', 'url': 'https://example.com/feed/', 'enabled': True}]
        client = NewsClient(sources=sources, max_articles=3)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert len(result['data']['articles']) == 3
    
    @patch('src.api_clients.news.feedparser.parse')
    def test_fetch_parse_error(self, mock_parse):
        """Test handling of RSS feed parse error."""
        # Setup mock to indicate parse error
        mock_feed = Mock()
        mock_feed.bozo = True  # Indicates parse failure
        mock_parse.return_value = mock_feed
        
        # Execute
        sources = [{'name': 'Bad Feed', 'url': 'https://bad.com/feed/', 'enabled': True}]
        client = NewsClient(sources=sources, max_articles=5)
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.api_clients.news.feedparser.parse')
    def test_fetch_partial_failure(self, mock_parse):
        """Test graceful degradation when some sources fail."""
        def parse_side_effect(url):
            feed = Mock()
            if 'good' in url:
                feed.bozo = False
                entry = Mock(
                    title='Good Article',
                    link='https://good.com/1',
                    published_parsed=(2025, 10, 31, 12, 0, 0, 3, 304, 0)
                )
                entry.get = lambda key, default=None, e=entry: getattr(e, key, default)
                feed.entries = [entry]
            else:
                feed.bozo = True  # Parse failure
            return feed
        
        mock_parse.side_effect = parse_side_effect
        
        # Execute
        sources = [
            {'name': 'Good Source', 'url': 'https://good.com/feed/', 'enabled': True},
            {'name': 'Bad Source', 'url': 'https://bad.com/feed/', 'enabled': True}
        ]
        client = NewsClient(sources=sources, max_articles=5)
        result = client.fetch()
        
        # Assert - should still succeed with partial data
        assert result['success'] is True
        assert len(result['data']['articles']) == 1
        assert result['data']['source_count'] == 1
    
    def test_format_for_display_success(self):
        """Test formatting of successful news data."""
        client = NewsClient(sources=[], max_articles=5)
        
        result = {
            'success': True,
            'data': {
                'articles': [
                    {
                        'title': 'Test Article',
                        'source': 'TechCrunch',
                        'link': 'https://example.com/article',
                        'published': '2025-10-31'
                    }
                ]
            }
        }
        
        formatted = client.format_for_display(result)
        
        assert 'Test Article' in formatted
        assert 'TechCrunch' in formatted
        assert 'https://example.com/article' in formatted
        assert '<a href=' in formatted
    
    def test_format_for_display_error(self):
        """Test formatting of error response."""
        client = NewsClient(sources=[], max_articles=5)
        
        result = {
            'success': False,
            'error': 'News unavailable'
        }
        
        formatted = client.format_for_display(result)
        
        assert 'unavailable' in formatted.lower()
    
    def test_format_date_valid(self):
        """Test date formatting with valid date tuple."""
        client = NewsClient(sources=[], max_articles=5)
        
        date_tuple = (2025, 10, 31, 12, 30, 45, 0, 304, 0)
        formatted = client._format_date(date_tuple)
        
        assert formatted == "2025-10-31"
    
    def test_format_date_invalid(self):
        """Test date formatting with invalid/missing date."""
        client = NewsClient(sources=[], max_articles=5)
        
        assert client._format_date(None) == "Recent"
        assert client._format_date([]) == "Recent"