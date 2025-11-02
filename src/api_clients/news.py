"""
News API Client - RSS Feed Aggregation.

Fetches tech news from multiple RSS feeds (no API key needed!).
This replaces NewsAPI which has production limitations on free tier.
"""

from typing import Dict, Any, List
from datetime import datetime
import feedparser

from .base import BaseAPIClient


class NewsClient(BaseAPIClient):
    """
    Client for fetching news via RSS feeds.
    
    Aggregates headlines from multiple tech news sources.
    No API key required - uses public RSS feeds.
    """
    
    def __init__(self, sources: List[Dict[str, Any]], max_articles: int = 5):
        """
        Initialize news client.
        
        Args:
            sources: List of news sources with 'name', 'url', and 'enabled' keys
            max_articles: Maximum total articles to fetch across all sources
        """
        super().__init__(name="News RSS")
        self.sources = [s for s in sources if s.get('enabled', True)]
        self.max_articles = max_articles
    
    def fetch(self) -> Dict[str, Any]:
        """
        Fetch news headlines from RSS feeds.
        
        Returns:
            Dictionary with success status and list of articles
            
        Example success response:
            {
                'success': True,
                'data': {
                    'articles': [
                        {
                            'title': 'Article title',
                            'source': 'TechCrunch',
                            'link': 'https://...',
                            'published': '2025-10-31'
                        },
                        ...
                    ]
                }
            }
        """
        all_articles = []
        successful_sources = 0
        
        for source in self.sources:
            try:
                articles = self._fetch_from_source(source)
                all_articles.extend(articles)
                successful_sources += 1
                
            except Exception as e:
                self.logger.warning(
                    f"Failed to fetch from {source['name']}: {str(e)}"
                )
                continue
        
        if successful_sources == 0:
            self.logger.error("Failed to fetch from all news sources")
            return {
                'success': False,
                'error': 'Top news headlines are temporarily unavailable.'
            }
        
        # Sort by published date (most recent first) and limit
        all_articles.sort(key=lambda x: x.get('published_parsed', ''), reverse=True)
        top_articles = all_articles[:self.max_articles]
        
        self.logger.info(
            f"✓ Fetched {len(top_articles)} articles from "
            f"{successful_sources} sources"
        )
        
        return {
            'success': True,
            'data': {
                'articles': top_articles,
                'source_count': successful_sources
            }
        }
    
    def _fetch_from_source(self, source: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Fetch articles from a single RSS feed.
        
        Args:
            source: Dictionary with 'name' and 'url' keys
            
        Returns:
            List of article dictionaries
        """
        self.logger.debug(f"Fetching from {source['name']}")
        
        # Parse RSS feed
        feed = feedparser.parse(source['url'])
        
        if feed.bozo:  # feedparser sets this flag if parsing failed
            raise ValueError(f"Failed to parse feed: {source['name']}")
        
        articles = []
        for entry in feed.entries[:3]:  # Get top 3 from each source
            article = {
                'title': entry.get('title', 'No title'),
                'source': source['name'],
                'link': entry.get('link', '#'),
                'published': self._format_date(entry.get('published_parsed')),
                'published_parsed': entry.get('published_parsed', '')
            }
            articles.append(article)
        
        return articles
    
    def _format_date(self, date_tuple) -> str:
        """
        Format RSS date tuple to readable string.
        
        Args:
            date_tuple: Time tuple from feedparser
            
        Returns:
            Formatted date string (YYYY-MM-DD) or "Recent"
        """
        if not date_tuple:
            return "Recent"
        
        try:
            dt = datetime(*date_tuple[:6])
            return dt.strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            return "Recent"
    
    def format_for_display(self, data: Dict[str, Any]) -> str:
        """
        Format news articles for HTML display.
        
        Args:
            data: News data dictionary from fetch()
            
        Returns:
            Formatted HTML string
        """
        if not data.get('success'):
            return data.get('error', 'News headlines unavailable')
        
        articles = data['data']['articles']
        
        if not articles:
            return "No recent articles found."
        
        # Format as bullet list with links
        html_parts = []
        for article in articles:
            html_parts.append(
                f"• <a href='{article['link']}' target='_blank'>"
                f"{article['title']}</a> "
                f"<span style='color: #888; font-size: 0.9em;'>"
                f"({article['source']})</span>"
            )
        
        return "<br>".join(html_parts)