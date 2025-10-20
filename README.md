# Daily Digest Generator 📰📈☀️

This repository contains a Python script that generates a daily HTML digest featuring local weather, top tech news headlines, and a stock market snapshot.

The entire process is automated to run daily using GitHub Actions.

## Data Sources

| Feature | API Used | Note |
| :--- | :--- | :--- |
| **Local Weather** | OpenWeatherMap | Uses a hardcoded location (San Jose, US). |
| **Tech News** | NewsAPI | Fetches top headlines for the "technology" topic. |
| **Stock Data** | Alpha Vantage | Fetches quotes for AAPL and GOOGL, with a 13-second rate-limit delay between calls. |
| **Fun Fact** | Numbers API | Provides a random trivia fact. |

## Automation

The digest is updated daily at 8:00 AM UTC via the GitHub Actions workflow defined in `.github/workflows/main.yml`. The resulting HTML file is committed back to the repository.
