"""
Integration Tests for Daily Digest Generator.

Tests the complete workflow from configuration to HTML generation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.main import DigestGenerator


class TestDigestGeneratorIntegration:
    """Integration test suite for complete digest generation."""
    
    @patch('src.main.load_config')
    @patch('src.api_clients.weather.WeatherClient.fetch')
    @patch('src.api_clients.news.NewsClient.fetch')
    @patch('src.api_clients.stocks.StocksClient.fetch')
    @patch('src.api_clients.quotes.QuotesClient.fetch')
    @patch('src.api_clients.word.WordClient.fetch')
    def test_successful_digest_generation(
        self, mock_word, mock_quotes, mock_stocks, mock_news, mock_weather,
        mock_load_config, mock_config, tmp_path
    ):
        """Test complete successful digest generation."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_config.output = {'filename': str(tmp_path / 'output.html'), 'title': 'Test'}
        
        # Mock successful API responses
        mock_weather.return_value = {
            'success': True,
            'data': {'temperature': 72, 'description': 'sunny', 'city': 'Test', 'country': 'TC'}
        }
        mock_news.return_value = {
            'success': True,
            'data': {'articles': [{'title': 'Test', 'source': 'Test', 'link': '#', 'published': '2025-10-31'}]}
        }
        mock_stocks.return_value = {
            'success': True,
            'data': {'quotes': [{'symbol': 'TEST', 'price': 100, 'change_percent': 1, 'direction': 'up'}], 'failed': []}
        }
        mock_quotes.return_value = {
            'success': True,
            'data': {'text': 'Test quote', 'author': 'Test Author'}
        }
        mock_word.return_value = {
            'success': True,
            'data': {'word': 'test', 'definition': 'A test word', 'source': 'test'}
        }
        
        # Execute
        generator = DigestGenerator(config_path="mock_config.yaml")
        success = generator.run()
        
        # Assert
        assert success is True
        
        # Check that output file was created
        output_file = Path(tmp_path / 'output.html')
        assert output_file.exists()
        
        # Check HTML content
        html_content = output_file.read_text()
        assert '<html' in html_content
        assert 'Test Digest' in html_content or 'Daily Digest' in html_content
        assert 'sunny' in html_content
        assert 'Test quote' in html_content
    
    @patch('src.main.load_config')
    @patch('src.api_clients.weather.WeatherClient.fetch')
    @patch('src.api_clients.news.NewsClient.fetch')
    @patch('src.api_clients.stocks.StocksClient.fetch')
    @patch('src.api_clients.quotes.QuotesClient.fetch')
    @patch('src.api_clients.word.WordClient.fetch')
    def test_partial_failure_still_generates_digest(
        self, mock_word, mock_quotes, mock_stocks, mock_news, mock_weather,
        mock_load_config, mock_config, tmp_path
    ):
        """Test that digest is generated even when some APIs fail."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_config.output = {'filename': str(tmp_path / 'output.html'), 'title': 'Test'}
        
        # Mock mixed success/failure responses
        mock_weather.return_value = {
            'success': True,
            'data': {'temperature': 72, 'description': 'sunny', 'city': 'Test', 'country': 'TC'}
        }
        mock_news.return_value = {
            'success': False,
            'error': 'News unavailable'
        }
        mock_stocks.return_value = {
            'success': True,
            'data': {'quotes': [{'symbol': 'TEST', 'price': 100, 'change_percent': 1, 'direction': 'up'}], 'failed': []}
        }
        mock_quotes.return_value = {
            'success': False,
            'error': 'Quotes unavailable'
        }
        mock_word.return_value = {
            'success': True,
            'data': {'word': 'test', 'definition': 'A test', 'source': 'test'}
        }
        
        # Execute
        generator = DigestGenerator(config_path="mock_config.yaml")
        success = generator.run()
        
        # Assert - should still succeed with partial data
        assert success is True
        
        output_file = Path(tmp_path / 'output.html')
        assert output_file.exists()
        
        html_content = output_file.read_text()
        assert 'sunny' in html_content  # Successful API
        assert 'unavailable' in html_content.lower()  # Failed APIs show error messages
    
    @patch('src.main.load_config')
    @patch('src.api_clients.weather.WeatherClient.fetch')
    @patch('src.api_clients.news.NewsClient.fetch')
    @patch('src.api_clients.stocks.StocksClient.fetch')
    @patch('src.api_clients.quotes.QuotesClient.fetch')
    @patch('src.api_clients.word.WordClient.fetch')
    def test_all_apis_fail_generates_error_page(
        self, mock_word, mock_quotes, mock_stocks, mock_news, mock_weather,
        mock_load_config, mock_config, tmp_path
    ):
        """Test that error page is generated when all APIs fail."""
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_config.output = {'filename': str(tmp_path / 'output.html'), 'title': 'Test'}
        
        # Mock all failures
        for mock_api in [mock_weather, mock_news, mock_stocks, mock_quotes, mock_word]:
            mock_api.return_value = {'success': False, 'error': 'API unavailable'}
        
        # Execute
        generator = DigestGenerator(config_path="mock_config.yaml")
        success = generator.run()
        
        # Assert - should return False but still create error page
        assert success is False
        
        output_file = Path(tmp_path / 'output.html')
        assert output_file.exists()
        
        html_content = output_file.read_text()
        assert 'error' in html_content.lower() or 'unavailable' in html_content.lower()
    
    @patch('src.main.load_config')
    def test_initialization_creates_all_clients(self, mock_load_config, mock_config):
        """Test that all API clients are initialized."""
        mock_load_config.return_value = mock_config
        
        generator = DigestGenerator(config_path="mock_config.yaml")
        
        # Assert all clients were created
        assert 'weather' in generator.clients
        assert 'news' in generator.clients
        assert 'stocks' in generator.clients
        assert 'quotes' in generator.clients
        assert 'word' in generator.clients
        assert len(generator.clients) == 5
    
    @patch('src.main.load_config')
    @patch('src.api_clients.weather.WeatherClient.fetch')
    @patch('src.api_clients.news.NewsClient.fetch')
    @patch('src.api_clients.stocks.StocksClient.fetch')
    @patch('src.api_clients.quotes.QuotesClient.fetch')
    @patch('src.api_clients.word.WordClient.fetch')
    def test_html_contains_all_sections(
        self, mock_word, mock_quotes, mock_stocks, mock_news, mock_weather,
        mock_load_config, mock_config, tmp_path
    ):
        """Test that generated HTML contains all expected sections."""
        # Setup
        mock_load_config.return_value = mock_config
        mock_config.output = {'filename': str(tmp_path / 'output.html'), 'title': 'Test Digest'}
        
        # Mock all successful
        mock_weather.return_value = {'success': True, 'data': {'temperature': 72, 'description': 'clear', 'city': 'Test', 'country': 'TC'}}
        mock_news.return_value = {'success': True, 'data': {'articles': [{'title': 'News', 'source': 'Test', 'link': '#', 'published': '2025-10-31'}]}}
        mock_stocks.return_value = {'success': True, 'data': {'quotes': [{'symbol': 'AAPL', 'price': 150, 'change_percent': 1, 'direction': 'up'}], 'failed': []}}
        mock_quotes.return_value = {'success': True, 'data': {'text': 'Quote', 'author': 'Author'}}
        mock_word.return_value = {'success': True, 'data': {'word': 'word', 'definition': 'definition', 'source': 'test'}}
        
        # Execute
        generator = DigestGenerator(config_path="mock_config.yaml")
        generator.run()
        
        # Assert
        html_content = Path(tmp_path / 'output.html').read_text()
        
        # Check for section headers
        assert 'Weather' in html_content or 'weather' in html_content.lower()
        assert 'News' in html_content or 'news' in html_content.lower()
        assert 'Stock' in html_content or 'stock' in html_content.lower()
        assert 'Quote' in html_content or 'quote' in html_content.lower()
        assert 'Word' in html_content or 'word' in html_content.lower()
        
        # Check for actual data
        assert 'clear' in html_content
        assert 'AAPL' in html_content
        assert 'Quote' in html_content
