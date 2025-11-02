"""
Configuration management for Daily Digest.

Loads settings from:
1. config.yaml - User preferences and feature flags
2. .env file - API keys and secrets

Validates required API keys and provides safe defaults.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv

from .utils.logger import setup_logger

logger = setup_logger(__name__)


class Config:
    """
    Centralized configuration manager.
    
    Loads configuration from YAML and environment variables,
    validates required settings, and provides easy access.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config.yaml file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._api_keys: Dict[str, Optional[str]] = {}
        
        # Load configuration
        self._load_env()
        self._load_yaml()
        self._load_api_keys()
        self._validate()
    
    def _load_env(self):
        """Load environment variables from .env file."""
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
            logger.info("Loaded environment variables from .env")
        else:
            logger.warning(".env file not found - using system environment variables")
    
    def _load_yaml(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            sys.exit(1)
        
        try:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config: {e}")
            sys.exit(1)
    
    def _load_api_keys(self):
        """Load API keys from environment variables."""
        self._api_keys = {
            'openweather': os.getenv('OPENWEATHER_API_KEY'),
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY'),
            'wordnik': os.getenv('WORDNIK_API_KEY'),  # Optional
        }
    
    def _validate(self):
        """Validate required configuration and API keys."""
        required_keys = ['openweather', 'alpha_vantage']
        missing_keys = []
        
        for key in required_keys:
            if not self._api_keys.get(key):
                missing_keys.append(key.upper())
        
        if missing_keys:
            logger.error("Missing required API keys:")
            for key in missing_keys:
                logger.error(f"  - {key}_API_KEY")
            logger.error("\nPlease set these in your .env file")
            logger.error("See .env.example for template")
            sys.exit(1)
        
        # Warn about optional keys
        if not self._api_keys.get('wordnik'):
            logger.warning(
                "WORDNIK_API_KEY not set - will use fallback Dictionary API"
            )
        
        logger.info("✓ All required API keys validated")
    
    # Convenience property accessors
    
    @property
    def location(self) -> Dict[str, str]:
        """Get location settings."""
        return self._config.get('location', {})
    
    @property
    def stocks(self) -> Dict[str, Any]:
        """Get stock settings."""
        return self._config.get('stocks', {})
    
    @property
    def news(self) -> Dict[str, Any]:
        """Get news settings."""
        return self._config.get('news', {})
    
    @property
    def quotes(self) -> Dict[str, Any]:
        """Get quotes settings."""
        return self._config.get('quotes', {})
    
    @property
    def word_of_the_day(self) -> Dict[str, Any]:
        """Get word of the day settings."""
        return self._config.get('word_of_the_day', {})
    
    @property
    def retry(self) -> Dict[str, Any]:
        """Get retry settings."""
        return self._config.get('retry', {
            'max_attempts': 3,
            'initial_delay': 1,
            'backoff_multiplier': 2
        })
    
    @property
    def logging_config(self) -> Dict[str, str]:
        """Get logging settings."""
        return self._config.get('logging', {
            'level': 'INFO',
            'format': 'detailed'
        })
    
    @property
    def output(self) -> Dict[str, str]:
        """Get output settings."""
        return self._config.get('output', {
            'filename': 'index.html',
            'title': 'Daily Digest'
        })
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a service.
        
        Args:
            service: Service name (openweather, alpha_vantage, wordnik)
            
        Returns:
            API key string or None if not set
        """
        return self._api_keys.get(service.lower())
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Dot-notation key (e.g., 'stocks.symbols')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value


# Global config instance (initialized when imported)
config: Optional[Config] = None


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load and return global configuration instance.
    
    Args:
        config_path: Path to config.yaml
        
    Returns:
        Config instance
    """
    global config
    config = Config(config_path)
    return config