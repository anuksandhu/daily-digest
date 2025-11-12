# Daily Digest Generator V2.0 📰📈☀️

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Testing: pytest](https://img.shields.io/badge/testing-pytest-green.svg)](https://docs.pytest.org/)

A robust, modular daily digest automation system that fetches data from multiple APIs and generates a professional HTML digest page. Built with modern software engineering best practices and designed for automated deployment via GitHub Actions.

## ✨ Features

- **📊 Multi-Source Data Aggregation**
  - Real-time weather from OpenWeatherMap
  - Tech news from RSS feeds (TechCrunch, Hacker News, The Verge)
  - Stock quotes with rate limiting
  - Daily inspirational quote
  - Word of the day with intelligent fallbacks

- **🏗️ Modern Architecture**
  - Modular, object-oriented design
  - Clean separation of concerns
  - Comprehensive error handling
  - Retry logic with exponential backoff
  - Centralized logging

- **🧪 Well-Tested**
  - Unit tests for all components
  - Integration tests for full workflow
  - 70%+ code coverage
  - Mocked external API calls

- **⚙️ Highly Configurable**
  - YAML-based configuration
  - Environment variable management
  - Customizable data sources
  - Flexible output formatting

- **🤖 CI/CD Ready**
  - GitHub Actions integration
  - Automated testing and linting
  - Scheduled daily updates
  - GitHub Pages deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- API keys (see below)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/daily-digest-v2.git
   cd daily-digest-v2
   ```

2. **Create virtual environment (recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**

   ```bash
   cp .env.example .env

   # Edit .env and add your API keys
   ```

5. **Run the digest generator**

   ```bash
   python -m src
   ```

## 🧪 Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
pytest

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only

# Generate HTML coverage report
pytest --cov-report=html
```

## 📝 License

This project is available for portfolio and educational purposes.

---

**Built with passion using Python and modern software practices.**
