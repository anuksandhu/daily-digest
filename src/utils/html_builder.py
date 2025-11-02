"""
HTML Builder - Generates the Daily Digest HTML page.

Separates presentation logic from business logic.
Clean, responsive HTML with inline CSS for maximum compatibility.
"""

from datetime import datetime
from typing import Dict, Any


def build_digest_html(
    title: str,
    weather_html: str,
    news_html: str,
    stocks_html: str,
    quote_html: str,
    word_html: str
) -> str:
    """
    Build complete HTML digest page.
    
    Args:
        title: Page title
        weather_html: Formatted weather content
        news_html: Formatted news content
        stocks_html: Formatted stock content
        quote_html: Formatted quote content
        word_html: Formatted word content
        
    Returns:
        Complete HTML document as string
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #fff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .timestamp {{
            color: #777;
            font-size: 0.95em;
            font-style: italic;
        }}
        
        .section {{
            margin-bottom: 35px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .section h2 {{
            color: #555;
            font-size: 1.5em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-content {{
            color: #666;
            font-size: 1.05em;
            line-height: 1.8;
        }}
        
        .section-content a {{
            color: #667eea;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }}
        
        .section-content a:hover {{
            border-bottom-color: #667eea;
        }}
        
        /* Section-specific styling */
        .weather {{
            background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
            border-left-color: #00acc1;
        }}
        
        .news {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-left-color: #fb8c00;
        }}
        
        .stocks {{
            background: linear-gradient(135deg, #f0fff4 0%, #c8e6c9 100%);
            border-left-color: #43a047;
        }}
        
        .quote {{
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border-left-color: #8e24aa;
        }}
        
        .word {{
            background: linear-gradient(135deg, #fff9c4 0%, #fff59d 100%);
            border-left-color: #fbc02d;
        }}
        
        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #999;
            font-size: 0.9em;
        }}
        
        footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        /* Responsive design */
        @media (max-width: 600px) {{
            .container {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 1.8em;
            }}
            
            .section {{
                padding: 15px;
            }}
        }}
        
        /* Print styles */
        @media print {{
            body {{
                background: white;
            }}
            
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 {title}</h1>
            <p class="timestamp">Generated on {timestamp}</p>
        </header>

        <div class="section weather">
            <h2>☀️ Local Weather</h2>
            <div class="section-content">
                {weather_html}
            </div>
        </div>
        
        <div class="section news">
            <h2>📰 Top Tech News</h2>
            <div class="section-content">
                {news_html}
            </div>
        </div>

        <div class="section stocks">
            <h2>📈 Stock Market Snapshot</h2>
            <div class="section-content">
                {stocks_html}
            </div>
        </div>

        <div class="section quote">
            <h2>💭 Quote of the Day</h2>
            <div class="section-content">
                {quote_html}
            </div>
        </div>
        
        <div class="section word">
            <h2>📚 Word of the Day</h2>
            <div class="section-content">
                {word_html}
            </div>
        </div>

        <footer>
            <p>
                Automated by a Python script via 
                <a href="https://github.com/features/actions" target="_blank">GitHub Actions</a>
            </p>
            <p style="margin-top: 10px; font-size: 0.85em;">
                Built with ❤️ using Python, APIs, and modern software practices
            </p>
        </footer>
    </div>
</body>
</html>"""
    
    return html


def build_error_html(title: str, error_message: str) -> str:
    """
    Build error page HTML.
    
    Args:
        title: Page title
        error_message: Error message to display
        
    Returns:
        Error page HTML
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Error</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        
        .error-container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 600px;
            text-align: center;
        }}
        
        h1 {{
            color: #e74c3c;
            font-size: 2em;
            margin-bottom: 20px;
        }}
        
        p {{
            color: #666;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>⚠️ Generation Failed</h1>
        <p>{error_message}</p>
        <p class="timestamp">Attempted: {timestamp}</p>
    </div>
</body>
</html>"""
    
    return html