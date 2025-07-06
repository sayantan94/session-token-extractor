import json
import time
import os
from playwright.sync_api import sync_playwright
from constants import WEBSITE_URL, WEBSITE_USERNAME, WEBSITE_PASSWORD, CONFIG_FILE_PATH, CONFIG_FILE_TYPE, CONFIG_TOKEN_KEY

class WebsiteLoginAutomation:
    def __init__(self, login_url, headless=True):
        """
        Initialize the automation with login URL and browser settings

        Args:
            login_url: The URL of the login page
            headless: Run browser in headless mode (True) or visible mode (False)
        """
        self.login_url = login_url
        self.headless = headless
        self.username = WEBSITE_USERNAME
        self.password = WEBSITE_PASSWORD

        if not self.username or not self.password:
            raise ValueError("Please set WEBSITE_USERNAME and WEBSITE_PASSWORD in constants.py file")

    def login_and_get_tokens(self, username_selector='input[name="username"]',
                             password_selector='input[name="password"]',
                             submit_selector='button[type="submit"]',
                             wait_after_login=None):
        """
        Login to website and extract all possible session tokens

        Args:
            username_selector: CSS selector for username input
            password_selector: CSS selector for password input
            submit_selector: CSS selector for submit button
            wait_after_login: Element or URL pattern to wait for after login

        Returns:
            Dictionary containing all found tokens from various storage locations
        """
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()

            try:
                print(f"Navigating to {self.login_url}")
                page.goto(self.login_url)

                # Wait for page to load
                page.wait_for_load_state('networkidle')

                # Take screenshot before login (for debugging)
                if not self.headless:
                    page.screenshot(path='before_login.png')

                print("Filling login form...")
                # Fill username
                page.wait_for_selector(username_selector, timeout=10000)
                page.fill(username_selector, self.username)

                # Fill password
                page.fill(password_selector, self.password)

                # Click submit
                page.click(submit_selector)

                print("Waiting for login to complete...")
                # Wait for navigation or specific element after login
                if wait_after_login:
                    if wait_after_login.startswith('http') or wait_after_login.startswith('/'):
                        # Wait for URL change
                        page.wait_for_url(wait_after_login, timeout=15000)
                    else:
                        # Wait for element
                        page.wait_for_selector(wait_after_login, timeout=15000)
                else:
                    # Generic wait for network idle
                    page.wait_for_load_state('networkidle')
                    time.sleep(2)  # Additional wait for JS to complete

                # Take screenshot after login (for debugging)
                if not self.headless:
                    page.screenshot(path='after_login.png')

                print("Extracting tokens...")
                # Extract all possible token locations
                tokens = self._extract_all_tokens(page, context)

                print("Login successful!")
                return tokens

            except Exception as e:
                print(f"Error during login: {e}")
                if not self.headless:
                    page.screenshot(path='error_screenshot.png')
                raise
            finally:
                browser.close()

    def _extract_all_tokens(self, page, context):
        """Extract tokens from all possible storage locations"""
        tokens = {}

        # 1. Extract cookies
        cookies = context.cookies()
        tokens['cookies'] = {}
        for cookie in cookies:
            tokens['cookies'][cookie['name']] = {
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie['path'],
                'expires': cookie.get('expires'),
                'httpOnly': cookie.get('httpOnly'),
                'secure': cookie.get('secure')
            }

        # 2. Extract localStorage
        try:
            local_storage = page.evaluate('''() => {
                const items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            }''')
            tokens['localStorage'] = local_storage
        except:
            tokens['localStorage'] = {}

        # 3. Extract sessionStorage
        try:
            session_storage = page.evaluate('''() => {
                const items = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    items[key] = sessionStorage.getItem(key);
                }
                return items;
            }''')
            tokens['sessionStorage'] = session_storage
        except:
            tokens['sessionStorage'] = {}

        # 4. Look for common token patterns in page content
        try:
            # Check for tokens in meta tags
            meta_tokens = page.evaluate('''() => {
                const metas = document.querySelectorAll('meta[name*="token"], meta[name*="csrf"]');
                const tokens = {};
                metas.forEach(meta => {
                    tokens[meta.getAttribute('name')] = meta.getAttribute('content');
                });
                return tokens;
            }''')
            tokens['metaTags'] = meta_tokens

            # Check for tokens in script variables (common patterns)
            script_tokens = page.evaluate('''() => {
                const tokens = {};
                // Common global variable names for tokens
                const tokenVars = ['token', 'authToken', 'sessionToken', 'csrfToken', 'apiToken', 'accessToken'];
                tokenVars.forEach(varName => {
                    if (window[varName]) {
                        tokens[varName] = window[varName];
                    }
                });
                return tokens;
            }''')
            tokens['scriptVariables'] = script_tokens
        except:
            pass

        return tokens

    def find_session_token(self, tokens):
        """
        Search for session token in extracted data

        Args:
            tokens: Dictionary of extracted tokens

        Returns:
            The most likely session token value
        """
        # Common session token names
        session_names = [
            'session', 'sessionid', 'session_id', 'sessiontoken', 'session_token',
            'phpsessid', 'jsessionid', 'aspsessionid', 'sid', 'connect.sid',
            'auth_token', 'authtoken', 'authorization', 'x-auth-token'
        ]

        # Search in cookies first (most common)
        for cookie_name, cookie_data in tokens.get('cookies', {}).items():
            if any(session_name in cookie_name.lower() for session_name in session_names):
                return {
                    'type': 'cookie',
                    'name': cookie_name,
                    'value': cookie_data['value'],
                    'full_data': cookie_data
                }

        # Search in localStorage
        for key, value in tokens.get('localStorage', {}).items():
            if any(session_name in key.lower() for session_name in session_names):
                return {
                    'type': 'localStorage',
                    'name': key,
                    'value': value
                }

        # Search in sessionStorage
        for key, value in tokens.get('sessionStorage', {}).items():
            if any(session_name in key.lower() for session_name in session_names):
                return {
                    'type': 'sessionStorage',
                    'name': key,
                    'value': value
                }

        return None

    def save_tokens_to_file(self, tokens, filename='extracted_tokens.json'):
        """Save extracted tokens to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(tokens, f, indent=2)
        print(f"Tokens saved to {filename}")

    def update_config_file(self, token_value, config_path=CONFIG_FILE_PATH, token_key=CONFIG_TOKEN_KEY):
        """
        Update configuration file with the session token
        
        Args:
            token_value: The session token value to update
            config_path: Path to the configuration file
            token_key: Key name for the token in the config file
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Read existing config or create new one
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            print(config)
            # Update the token
            config[token_key] = token_value
            
            # Write back to file
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"Updated {token_key} in {config_path}")
            
        except Exception as e:
            print(f"Error updating config file: {e}")
            raise



if __name__ == "__main__":
    # Initialize automation
    automation = WebsiteLoginAutomation(
        login_url=WEBSITE_URL,
        headless=False  # Set to True for headless mode
    )

    try:
        # Login and get tokens
        # Adjust selectors based on your website's HTML
        tokens = automation.login_and_get_tokens(
            username_selector='#username',  # Using ID selector
            password_selector='#password',  # Using ID selector
            submit_selector='button:has-text("Login")',  # Button with Login text
            wait_after_login=None  # Let it wait for network idle
        )

        automation.update_config_file(tokens['sessionStorage']['token'])

        # Pretty print all tokens
        print("\n=== All Extracted Tokens ===")
        print(json.dumps(tokens, indent=2))

    except Exception as e:
        print(f"Automation failed: {e}")