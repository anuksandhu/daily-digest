import os
import requests
import time
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# --- Step 1: Fetch Weather Data ---
def fetch_weather(location, api_key):
    """Fetches the current weather for a given location."""
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=imperial"
    
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()  
        data = response.json()
        
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        city = data['name']
        country = data['sys']['country']
        
        return f"{city}, {country}: {temp:.0f}°F with {description}."

    # Catch-all for network errors, including Timeout and raise_for_status()
#    except requests.exceptions.RequestException as e:
#        return f"Weather Error: Could not fetch data. {e}"

    except requests.exceptions.RequestException as e:
        return f"Weather data for {location} is temporarily unavailable."
    except KeyError:
        return "Error: Invalid data format received from weather API."
    
# --- Step 2: Fetch News Headlines ---
def fetch_news(topic, api_key):
    """Fetches top news headlines for a given topic."""
    api_url = f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey={api_key}&pageSize=3"
    
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        headlines = []
        for article in data['articles']:
            # We will use the URL later in the HTML email
            headlines.append(f"- {article['title']}")
        return "\n".join(headlines)

#    except requests.exceptions.RequestException as e:
#        return f"Error fetching news: {e}"
    
    except requests.exceptions.RequestException as e:
        return "Top news headlines are temporarily unavailable."
    except KeyError:
        return "Error: Invalid data format received from news API."

# --- Step 3: Fetch Stock Prices ---
def fetch_stocks(symbols, api_key):
    """Fetches the latest price for a list of stock symbols with a rate-limit delay."""
    reports = []
    # print("in fetch stock") #debug - removing debug prints now
    
    # We loop through symbols, but must add a delay to respect Alpha Vantage limits
    for i, symbol in enumerate(symbols):
        # Only pause BEFORE the second, third, etc., request.
        if i > 0:
            time.sleep(13) # Pause for 13 seconds to ensure we stay under the 5 req/min limit
            
        api_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        
        try:
            # Add a short timeout to prevent indefinite hangs
            response = requests.get(api_url, timeout=15) 
            response.raise_for_status()
            data = response.json()

            # Check for rate limit error in the response data itself
            if "Note" in data and "rate limit" in data["Note"]:
                 reports.append(f"{symbol}: API Rate Limit Hit - Waiting for next run.")
                 break # Stop processing symbols if we hit the limit
            
            # The key for the quote data is 'Global Quote'
            quote = data.get('Global Quote')
            if not quote:
                reports.append(f"{symbol}: Error fetching data (likely invalid symbol).")
                continue
            
            # ... rest of your successful parsing code remains the same ...
            price = float(quote['05. price'])
            change_percent_str = quote['10. change percent'].replace('%', '')
            change_percent = float(change_percent_str)
            
            # Add an emoji for visual indication of the price change
            emoji = "▲" if change_percent > 0 else "▼"
            reports.append(f"{symbol}: ${price:.2f} ({change_percent:.2f}%) {emoji}")

        except requests.exceptions.Timeout:
            reports.append(f"{symbol}: Stock data currently unavailable (API timeout).")
        except requests.exceptions.RequestException as e:
            # Keep this as a clear error for internal debugging
            reports.append(f"{symbol}: Network or Request failed: {e}") 
        except (KeyError, ValueError):
            reports.append(f"{symbol}: Error parsing data (Check API key/symbol).")
            
    # If BOTH symbols fail with a Timeout, replace the output with one clean message.
    stock_output = "\n".join(reports)
    
    if all("unavailable" in r for r in reports) and len(reports) == len(symbols):
        return "Market data is temporarily unavailable due to an external API issue. Please check back later."
    
    return stock_output

# --- Step 4: Fetch Daily Fun Fact ---
def fetch_fun_fact():
    """Fetches a random trivia fact from the Numbers API."""
    api_url = "http://numbersapi.com/random/trivia"
    
    try:
        # We don't need JSON; the API returns the fact as plain text
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        return response.text
    
#    except requests.exceptions.RequestException as e:
#        return f"Error fetching fun fact: {e}"
    except requests.exceptions.RequestException as e:
        return "A fun fact is not available right now. Try again later!"

# --- Step 5: Build the HTML Digest ---
def build_html_digest(weather_report, news_report, stock_report, fun_fact): 
    # ... rest of the function ...
    """
    Generates a full HTML page for the Daily Digest.
    """
    
    # We use basic inline CSS for a clean, professional look
    # and maximum compatibility for a static page.
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Automated Daily Digest</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; background-color: #f4f4f4; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            h1 {{ color: #0056b3; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            h2 {{ color: #555; margin-top: 20px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
            p, ul {{ line-height: 1.6; margin-bottom: 15px; }}
            .weather {{ background: #e0f7fa; padding: 10px; border-radius: 4px; }}
            .stock {{ background: #f0fff4; padding: 10px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Automated Daily Digest</h1>
            <p style="color: #777;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h2>☀️ Local Weather</h2>
            <div class="weather">
                <p>{weather_report}</p>
            </div>
            
            <h2>📰 Top Tech News</h2>
            <p style="white-space: pre-wrap;">{news_report}</p>

            <h2>📈 Stock Market Snapshot</h2>
            <div class="stock">
                <p style="white-space: pre-wrap;">{stock_report}</p>
            </div>

            <h2>🧠 Daily Fun Fact</h2>
            <div style="background: #fff3e0; padding: 10px; border-radius: 4px; border-left: 5px solid #ff9800;">
                <p><strong>Did you know?</strong> {fun_fact}</p>
            </div>
            
            <p style="text-align: center; font-size: 0.8em; color: #aaa; margin-top: 30px;">
                Automated by a Python Script via GitHub Actions
            </p>
        </div>
    </body>
    </html>
    """
    return html_content

# --- Main execution block ---
if __name__ == "__main__":
    
    # Retrieve API keys from environment
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    news_api_key = os.getenv("NEWS_API_KEY")
    stock_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

   # --- 1. Fetch Data (Updated with Fun Fact) ---
    weather_report = fetch_weather("San Jose,US", weather_api_key)
    news_report = fetch_news("technology", news_api_key)
    stock_report = fetch_stocks(["AAPL", "GOOGL"], stock_api_key)
    fun_fact = fetch_fun_fact() #new 
    
    # --- 2. Build HTML (Updated to pass Fun Fact) ---
    html_digest = build_html_digest(weather_report, news_report, stock_report, fun_fact)
 
    # --- 3. Write to File (The Web Publishing Step) ---
    try:
        with open("index.html", "w") as f:
            f.write(html_digest)
        print("SUCCESS: index.html has been generated.")
    except IOError as e:
        print(f"ERROR: Could not write index.html file: {e}")
