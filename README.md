# Session Token Extractor

A Python tool for extracting session tokens and authentication data from web applications using Playwright automation.

## Features

- Automated web login using Playwright
- Extracts tokens from multiple sources:
  - Cookies
  - Local Storage
  - Session Storage
  - HTTP Response Headers
- Configurable selectors for different login forms
- Headless and visible browser modes
- Saves extracted tokens to JSON file
- Debug mode with screenshots

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/session-token-extractor.git
cd session-token-extractor
```

2. Install dependencies:
```bash
pip install playwright
playwright install chromium
```

3. Configure your credentials:
```bash
cp constants_sample.py constants.py
```

Edit `constants.py` with your actual credentials:
```python
WEBSITE_URL = 'https://your-website-url.com/login'
WEBSITE_USERNAME = 'your_username'
WEBSITE_PASSWORD = 'your_password'
```
