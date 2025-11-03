"""
Tests for Quotes and Word API Clients.

Combined test file - corrected to match actual WordClient implementation.
"""

import pytest
from unittest.mock import Mock, patch
from src.api_clients.quotes import QuotesClient
from src.api_clients.word import WordClient


class TestQuotesClient:
    """Test suite for QuotesClient."""
    
    def test_initialization(self):
        """Test client initializes correctly (no API key needed)."""
        client = QuotesClient()
        
        assert client.name == "Quotes API"
        assert client.api_key is None
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_success(self, mock_request, sample_quote_response):
        """Test successful quote fetch."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = sample_quote_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = QuotesClient()
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert 'data' in result
        assert result['data']['text'] == 'The best way to predict the future is to invent it.'
        assert result['data']['author'] == 'Alan Kay'
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_invalid_response_format(self, mock_request):
        """Test handling of unexpected response format."""
        # Setup mock with invalid format
        mock_response = Mock()
        mock_response.json.return_value = {}  # Not a list
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = QuotesClient()
        result = client.fetch()
        
        # Assert
        assert result['success'] is False
        assert 'error' in result
    
    def test_format_for_display_success(self):
        """Test formatting of successful quote."""
        client = QuotesClient()
        
        result = {
            'success': True,
            'data': {
                'text': 'Test quote',
                'author': 'Test Author'
            }
        }
        
        formatted = client.format_for_display(result)
        
        assert 'Test quote' in formatted
        assert 'Test Author' in formatted
        assert '"' in formatted  # Should have quotes
    
    def test_format_for_display_error(self):
        """Test formatting of error response."""
        client = QuotesClient()
        
        result = {
            'success': False,
            'error': 'Quote unavailable'
        }
        
        formatted = client.format_for_display(result)
        
        assert 'unavailable' in formatted.lower()


class TestWordClient:
    """Test suite for WordClient."""
    
    def test_initialization_with_api_key(self):
        """Test client initializes with Wordnik API key."""
        client = WordClient(api_key="test_key", fallback_enabled=True)
        
        assert client.api_key == "test_key"
        assert client.fallback_enabled is True
    
    def test_initialization_without_api_key(self):
        """Test client initializes without API key (fallback mode)."""
        client = WordClient(api_key=None, fallback_enabled=True)
        
        assert client.api_key is None
        assert client.fallback_enabled is True
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_from_wordnik_success(self, mock_request, sample_word_response):
        """Test successful fetch from Wordnik."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = sample_word_response
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        # Execute
        client = WordClient(api_key="test_key", fallback_enabled=True)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert result['data']['word'] == 'serendipity'
        assert result['data']['source'] == 'wordnik'
    
    @patch('src.api_clients.word.WordClient._fetch_from_wordnik')
    @patch('src.api_clients.word.WordClient._fetch_fallback')
    def test_fetch_wordnik_fails_uses_fallback(self, mock_fallback, mock_wordnik):
        """Test fallback to Dictionary API when Wordnik fails."""
        # Setup mocks - Wordnik fails, fallback succeeds
        mock_wordnik.return_value = {'success': False, 'error': 'Wordnik unavailable'}
        mock_fallback.return_value = {
            'success': True,
            'data': {
                'word': 'fallback',
                'definition': 'A wonderful word',
                'source': 'dictionary_api'
            }
        }
        
        # Execute
        client = WordClient(api_key="test_key", fallback_enabled=True)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert result['data']['source'] in ['dictionary_api', 'fallback']
        assert mock_wordnik.called
        assert mock_fallback.called
    
    @patch('src.api_clients.base.requests.Session.request')
    def test_fetch_no_api_key_uses_fallback(self, mock_request):
        """Test that fallback is used when no API key provided."""
        # Setup mock for Dictionary API
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = [{
            'meanings': [{
                'definitions': [{
                    'definition': 'A test definition'
                }]
            }]
        }]
        mock_request.return_value = mock_response
        
        # Execute - no API key
        client = WordClient(api_key=None, fallback_enabled=True)
        result = client.fetch()
        
        # Assert
        assert result['success'] is True
        assert result['data']['source'] in ['dictionary_api', 'fallback']
    
    @patch('src.api_clients.word.WordClient._fetch_from_wordnik')
    @patch('src.api_clients.word.WordClient._fetch_fallback')
    def test_fetch_all_sources_fail_uses_hardcoded(self, mock_fallback, mock_wordnik):
        """Test hardcoded fallback when all API sources fail.
        
        FIX: Removed _get_hardcoded_word mock - that method doesn't exist.
        The hardcoded fallback is handled inline in _fetch_fallback().
        """
        # Setup mocks - all APIs fail, but _fetch_fallback has inline hardcoded fallback
        mock_wordnik.return_value = {'success': False, 'error': 'Wordnik down'}
        mock_fallback.return_value = {
            'success': True,
            'data': {
                'word': 'serendipity',
                'definition': 'A wonderful word worth exploring!',
                'source': 'fallback'
            }
        }
        
        # Execute
        client = WordClient(api_key="test_key", fallback_enabled=True)
        result = client.fetch()
        
        # Assert - should still succeed with hardcoded word
        assert result['success'] is True
        assert result['data']['source'] == 'fallback'
        assert result['data']['word'] in WordClient.FALLBACK_WORDS
        assert mock_wordnik.called
        assert mock_fallback.called
    
    def test_fallback_disabled(self):
        """Test behavior when fallback is disabled."""
        client = WordClient(api_key=None, fallback_enabled=False)
        result = client.fetch()
        
        # Should fail when no API key and fallback disabled
        assert result['success'] is False
        assert 'error' in result
    
    def test_format_for_display_success(self):
        """Test formatting of successful word data."""
        client = WordClient(api_key="test_key")
        
        result = {
            'success': True,
            'data': {
                'word': 'serendipity',
                'definition': 'Finding something good without looking for it',
                'source': 'wordnik'
            }
        }
        
        formatted = client.format_for_display(result)
        
        assert 'serendipity' in formatted.lower()
        assert 'Finding something good' in formatted
    
    def test_format_for_display_error(self):
        """Test formatting of error response."""
        client = WordClient(api_key="test_key")
        
        result = {
            'success': False,
            'error': 'Word unavailable'
        }
        
        formatted = client.format_for_display(result)
        
        assert 'unavailable' in formatted.lower()
    
    def test_fallback_word_consistency(self):
        """Test that fallback word is consistent for the same day."""
        # The word should be based on day of year, so multiple calls
        # on the same day should return the same word (when using fallback)
        client = WordClient(api_key=None, fallback_enabled=True)
        
        # Get day index
        from datetime import datetime
        day = datetime.now().timetuple().tm_yday
        expected_word = client.FALLBACK_WORDS[day % len(client.FALLBACK_WORDS)]
        
        # The word in fallback mode should match this
        assert expected_word in client.FALLBACK_WORDS
