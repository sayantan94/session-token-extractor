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
- Automatically updates configuration files with session tokens
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
cp constants.py.sample constants.py
```

Edit `constants.py` with your actual credentials:
```python
WEBSITE_URL = 'https://your-website-url.com/login'
WEBSITE_USERNAME = 'your_username'
WEBSITE_PASSWORD = 'your_password'

# Configuration file settings
CONFIG_FILE_PATH = '/etc/config/Config.json'
CONFIG_FILE_TYPE = 'json'
CONFIG_TOKEN_KEY = 'API_TOKEN'
```

## Configuration

### Configuration File Settings

The tool can automatically update configuration files with extracted session tokens. Configure these settings in `constants.py`:

- `CONFIG_FILE_PATH`: Path to the configuration file (default: `/etc/config/Config.json`)
- `CONFIG_FILE_TYPE`: Type of configuration file (default: `json`)
- `CONFIG_TOKEN_KEY`: Key name for the token in the config file 

The tool supports both JSON and text configuration files. When a session token is found, it will automatically update the specified configuration file.

## Usage

Run the token extractor:
```bash
python extractor.py
```

The script will:
1. Navigate to the specified login URL
2. Fill in credentials and submit the form
3. Extract session tokens from all available sources
4. Save all tokens to `extracted_tokens.json`
5. Automatically update the configuration file with the session token
6. Display the found session token details
