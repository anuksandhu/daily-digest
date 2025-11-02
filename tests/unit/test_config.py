"""
Tests for Configuration Module.

Tests configuration loading, validation, and API key management.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from src.config import Config, load_config


class TestConfig:
    """Test suite for Config class."""
    
    def test_load_valid_config(self, tmp_path):
        """Test loading a valid configuration file."""
        # Create temporary config file
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
location:
  city: "Test City"
  country: "TC"

stocks:
  symbols: ["TEST"]
  rate_limit_delay: 10

news:
  sources:
    - name: "Test Source"
      url: "https://example.com/feed"
      enabled: true
  max_articles: 5

quotes:
  source: "zenquotes"

word_of_the_day:
  fallback_enabled: true

output:
  filename: "test.html"
  title: "Test Digest"
""")
        
        # Create temporary .env
        env_file = tmp_path / ".env"
        env_file.write_text("""
OPENWEATHER_API_KEY=test_weather_key
ALPHA_VANTAGE_API_KEY=test_stock_key
""")
        
        # Load config
        with patch.dict(os.environ, {}, clear=True):
            config = Config(config_path=str(config_file))
        
        # Assert
        assert config.location['city'] == "Test City"
        assert config.stocks['symbols'] == ["TEST"]
        assert config.output['filename'] == "test.html"
    
    def test_missing_config_file(self):
        """Test behavior when config file doesn't exist."""
        with pytest.raises(SystemExit):
            Config(config_path="nonexistent.yaml")
    
    def test_invalid_yaml(self, tmp_path):
        """Test handling of invalid YAML syntax."""
        config_file = tmp_path / "bad_config.yaml"
        config_file.write_text("invalid: yaml: syntax: here")
        
        with pytest.raises(SystemExit):
            Config(config_path=str(config_file))
    
    def test_missing_required_api_keys(self, tmp_path):
        """Test validation fails when required API keys are missing."""
        # Create valid config
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
location:
  city: "Test"
  country: "TC"
stocks:
  symbols: ["TEST"]
""")
        
        # No .env file created
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                Config(config_path=str(config_file))
    
    def test_optional_api_key_warning(self, tmp_path, caplog):
        """Test that missing optional API keys generate warnings."""
        # Create config
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
location:
  city: "Test"
stocks:
  symbols: ["TEST"]
output:
  filename: "test.html"
""")
        
        # Only provide required keys
        with patch.dict(os.environ, {
            'OPENWEATHER_API_KEY': 'test1',
            'ALPHA_VANTAGE_API_KEY': 'test2'
        }, clear=True):
            config = Config(config_path=str(config_file))
            
            # Should have warning about WORDNIK_API_KEY
            assert config.get_api_key('wordnik') is None
    
    def test_get_api_key(self, mock_config):
        """Test getting API keys."""
        assert mock_config.get_api_key('openweather') == 'test_weather_key'
        assert mock_config.get_api_key('alpha_vantage') == 'test_stock_key'
        assert mock_config.get_api_key('wordnik') == 'test_wordnik_key'
        assert mock_config.get_api_key('nonexistent') is None
    
    def test_property_accessors(self, mock_config):
        """Test configuration property accessors."""
        assert mock_config.location['city'] == 'San Jose'
        assert mock_config.stocks['symbols'] == ['AAPL', 'GOOGL']
        assert mock_config.news['max_articles'] == 5
        assert mock_config.output['filename'] == 'test_output.html'
    
    def test_get_nested_value(self, mock_config):
        """Test getting nested configuration values."""
        assert mock_config.get('location.city') == 'San Jose'
        assert mock_config.get('stocks.symbols') == ['AAPL', 'GOOGL']
        assert mock_config.get('nonexistent.key', 'default') == 'default'
    
    def test_retry_defaults(self, mock_config):
        """Test that retry configuration has proper defaults."""
        retry = mock_config.retry
        assert retry['max_attempts'] == 3
        assert retry['initial_delay'] == 1
        assert retry['backoff_multiplier'] == 2
    
    def test_load_config_function(self, tmp_path):
        """Test the load_config convenience function."""
        # Create minimal config
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
location:
  city: "Test"
stocks:
  symbols: ["TEST"]
output:
  filename: "test.html"
""")
        
        with patch.dict(os.environ, {
            'OPENWEATHER_API_KEY': 'test1',
            'ALPHA_VANTAGE_API_KEY': 'test2'
        }, clear=True):
            config = load_config(str(config_file))
            
            assert isinstance(config, Config)
            assert config.location['city'] == "Test"
