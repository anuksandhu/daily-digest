"""
Daily Digest Generator - Main Application.

Orchestrates all API clients to generate a daily digest HTML page.

Architecture:
1. Load configuration
2. Initialize API clients
3. Fetch data from all sources
4. Build HTML digest
5. Write to output file
"""

import sys
from pathlib import Path
from typing import Dict, Any

from .config import load_config
from .utils.logger import setup_logger
from .utils.html_builder import build_digest_html, build_error_html
from .api_clients import (
    WeatherClient,
    NewsClient,
    StocksClient,
    QuotesClient,
    WordClient
)


class DigestGenerator:
    """
    Main application class that orchestrates digest generation.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize digest generator.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = setup_logger("daily_digest")
        self.logger.info("=" * 60)
        self.logger.info("Daily Digest Generator V2.0 - Starting")
        self.logger.info("=" * 60)
        
        # Load configuration
        try:
            self.config = load_config(config_path)
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
        
        # Initialize clients
        self.clients = self._initialize_clients()
    
    def _initialize_clients(self) -> Dict[str, Any]:
        """
        Initialize all API clients with configuration.
        
        Returns:
            Dictionary of initialized clients
        """
        self.logger.info("Initializing API clients...")
        
        clients = {}
        
        try:
            # Weather client
            location = self.config.location
            clients['weather'] = WeatherClient(
                api_key=self.config.get_api_key('openweather'),
                city=location['city'],
                country=location['country']
            )
            self.logger.info("✓ Weather client initialized")
            
            # News client (RSS - no API key needed!)
            clients['news'] = NewsClient(
                sources=self.config.news['sources'],
                max_articles=self.config.news['max_articles']
            )
            self.logger.info("✓ News client initialized")
            
            # Stocks client
            stocks_config = self.config.stocks
            clients['stocks'] = StocksClient(
                api_key=self.config.get_api_key('alpha_vantage'),
                symbols=stocks_config['symbols'],
                rate_limit_delay=stocks_config['rate_limit_delay']
            )
            self.logger.info("✓ Stocks client initialized")
            
            # Quotes client (no API key needed!)
            clients['quotes'] = QuotesClient()
            self.logger.info("✓ Quotes client initialized")
            
            # Word client (with optional Wordnik key)
            word_config = self.config.word_of_the_day
            clients['word'] = WordClient(
                api_key=self.config.get_api_key('wordnik'),
                fallback_enabled=word_config.get('fallback_enabled', True)
            )
            self.logger.info("✓ Word client initialized")
            
            self.logger.info(f"All {len(clients)} clients initialized successfully\n")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize clients: {e}")
            sys.exit(1)
        
        return clients
    
    def fetch_all_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch data from all API clients.
        
        Returns:
            Dictionary mapping client names to their results
        """
        self.logger.info("Fetching data from all sources...")
        self.logger.info("-" * 60)
        
        results = {}
        
        # Fetch from each client
        for name, client in self.clients.items():
            try:
                self.logger.info(f"Fetching {name}...")
                result = client.fetch()
                results[name] = result
                
                if result['success']:
                    self.logger.info(f"✓ {name.capitalize()} fetch succeeded")
                else:
                    self.logger.warning(
                        f"⚠ {name.capitalize()} fetch failed: {result.get('error')}"
                    )
                    
            except Exception as e:
                self.logger.error(f"✗ {name.capitalize()} fetch error: {e}")
                results[name] = {
                    'success': False,
                    'error': f'{name.capitalize()} is temporarily unavailable.'
                }
        
        self.logger.info("-" * 60)
        
        # Summary
        successful = sum(1 for r in results.values() if r['success'])
        total = len(results)
        self.logger.info(f"Fetch complete: {successful}/{total} sources successful\n")
        
        return results
    
    def build_html(self, results: Dict[str, Dict[str, Any]]) -> str:
        """
        Build HTML digest from fetched data.
        
        Args:
            results: Dictionary of fetch results from all clients
            
        Returns:
            Complete HTML document as string
        """
        self.logger.info("Building HTML digest...")
        
        # Format each section using client's format_for_display method
        weather_html = self.clients['weather'].format_for_display(results['weather'])
        news_html = self.clients['news'].format_for_display(results['news'])
        stocks_html = self.clients['stocks'].format_for_display(results['stocks'])
        quote_html = self.clients['quotes'].format_for_display(results['quotes'])
        word_html = self.clients['word'].format_for_display(results['word'])
        
        # Build complete HTML
        html = build_digest_html(
            title=self.config.output['title'],
            weather_html=weather_html,
            news_html=news_html,
            stocks_html=stocks_html,
            quote_html=quote_html,
            word_html=word_html
        )
        
        self.logger.info("✓ HTML digest built successfully\n")
        return html
    
    def write_output(self, html: str) -> bool:
        """
        Write HTML to output file.
        
        Args:
            html: Complete HTML document
            
        Returns:
            True if successful, False otherwise
        """
        output_path = Path(self.config.output['filename'])
        
        try:
            self.logger.info(f"Writing output to {output_path}...")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            file_size = output_path.stat().st_size
            self.logger.info(f"✓ Output written successfully ({file_size:,} bytes)")
            self.logger.info(f"✓ File location: {output_path.absolute()}\n")
            
            return True
            
        except IOError as e:
            self.logger.error(f"Failed to write output file: {e}")
            return False
    
    def run(self) -> bool:
        """
        Main execution flow.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch all data
            results = self.fetch_all_data()
            
            # Check if at least some data was fetched successfully
            successful_count = sum(1 for r in results.values() if r['success'])
            
            if successful_count == 0:
                self.logger.error("All API fetches failed - cannot generate digest")
                error_html = build_error_html(
                    title=self.config.output['title'],
                    error_message="Unable to fetch data from any source. Please try again later."
                )
                self.write_output(error_html)
                return False
            
            # Build HTML
            html = self.build_html(results)
            
            # Write to file
            success = self.write_output(html)
            
            if success:
                self.logger.info("=" * 60)
                self.logger.info("✓ Daily Digest generated successfully!")
                self.logger.info("=" * 60)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Unexpected error during generation: {e}")
            
            # Try to write error page
            try:
                error_html = build_error_html(
                    title=self.config.output['title'],
                    error_message=f"An unexpected error occurred: {str(e)}"
                )
                self.write_output(error_html)
            except Exception as write_error:
                self.logger.error(f"Failed to write error page: {write_error}")
            
            return False
        
        finally:
            # Clean up
            self.cleanup()
    
    def cleanup(self):
        """Close all client connections."""
        self.logger.debug("Cleaning up resources...")
        for client in self.clients.values():
            try:
                client.close()
            except Exception as e:
                self.logger.debug(f"Error closing client: {e}")


def main():
    """
    Entry point for the application.
    """
    generator = DigestGenerator()
    success = generator.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()