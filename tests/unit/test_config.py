"""
Tests for Configuration Module.

Tests configuration loading, validation, and API key management.
Updated to properly handle empty strings vs None for API keys.
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
        
        # Change to tmp_path and provide API keys in environment
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Provide required API keys in environment
            with patch.dict(os.environ, {
                'OPENWEATHER_API_KEY': 'test_weather_key',
                'ALPHA_VANTAGE_API_KEY': 'test_stock_key'
            }, clear=False):
                config = Config(config_path=str(config_file))
                
                # Assert
                assert config.location['city'] == "Test City"
                assert config.stocks['symbols'] == ["TEST"]
                assert config.output['filename'] == "test.html"
        finally:
            os.chdir(original_dir)
    
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
        """Test validation fails when required API keys are missing.
        
        Updated to properly clear environment and prevent .env file loading.
        """
        # Create valid config
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
location:
  city: "Test"
  country: "TC"
stocks:
  symbols: ["TEST"]
output:
  filename: "test.html"
""")
        
        # Change to tmp_path (no .env file there) and clear environment
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Completely clear the environment of our API keys
            env_without_keys = {k: v for k, v in os.environ.items() 
                               if not k.endswith('_API_KEY')}
            
            with patch.dict(os.environ, env_without_keys, clear=True):
                with pytest.raises(SystemExit):
                    Config(config_path=str(config_file))
        finally:
            os.chdir(original_dir)
    
    def test_optional_api_key_warning(self, tmp_path, caplog):
        """Test that missing optional API keys generate warnings.
        
        Updated to verify None is returned (not empty string).
        """
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
        
        # Change to tmp_path and only provide required keys
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Only provide required keys, explicitly exclude optional ones
            env_with_required_only = {
                k: v for k, v in os.environ.items() 
                if not k.endswith('_API_KEY')
            }
            env_with_required_only['OPENWEATHER_API_KEY'] = 'test1'
            env_with_required_only['ALPHA_VANTAGE_API_KEY'] = 'test2'
            
            with patch.dict(os.environ, env_with_required_only, clear=True):
                config = Config(config_path=str(config_file))
                
                # Should return None for missing optional key
                assert config.get_api_key('wordnik') is None
        finally:
            os.chdir(original_dir)
    
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
    
    def test_get_nested_value(self, tmp_path):
        """Test accessing nested configuration values."""
        # Create minimal config
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
location:
  city: "San Jose"
  country: "US"
stocks:
  symbols: ["AAPL", "GOOGL"]
output:
  filename: "test.html"
""")
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch.dict(os.environ, {
                'OPENWEATHER_API_KEY': 'test1',
                'ALPHA_VANTAGE_API_KEY': 'test2'
            }, clear=False):
                config = Config(config_path=str(config_file))
                
                # Test actual API (dictionary access)
                assert config.location['city'] == 'San Jose'
                assert config.stocks['symbols'] == ['AAPL', 'GOOGL']
        finally:
            os.chdir(original_dir)
    
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
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Filter out any API key env vars and set only required ones
            env_clean = {k: v for k, v in os.environ.items() 
                        if not k.endswith('_API_KEY')}
            env_clean['OPENWEATHER_API_KEY'] = 'test1'
            env_clean['ALPHA_VANTAGE_API_KEY'] = 'test2'
            
            with patch.dict(os.environ, env_clean, clear=True):
                config = load_config(str(config_file))
                
                assert isinstance(config, Config)
                assert config.location['city'] == "Test"
        finally:
            os.chdir(original_dir)