"""
Configuration module for the AI Agent.
Loads settings from environment variables.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ============================================
# OpenAI Configuration
# ============================================

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
OPENAI_IMAGE_MODEL = os.getenv('OPENAI_IMAGE_MODEL', 'dall-e-3')

# ============================================
# Telegram Configuration
# ============================================

TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Optional: Session file path for Telegram
TELEGRAM_SESSION_FILE = os.getenv('TELEGRAM_SESSION_FILE', 'telegram_session')

# ============================================
# Flask Backend Configuration
# ============================================

FLASK_API_URL = os.getenv('FLASK_API_URL', 'http://localhost:5000')
FLASK_PENDING_POSTS_ENDPOINT = f"{FLASK_API_URL}/api/pending-posts"

# ============================================
# Playwright Configuration
# ============================================

HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30000'))  # milliseconds
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# ============================================
# Agent Behavior Configuration
# ============================================

# Maximum number of messages to process from Telegram
MAX_MESSAGES_TO_PROCESS = int(os.getenv('MAX_MESSAGES_TO_PROCESS', '50'))

# Maximum number of URLs to process per run
MAX_URLS_TO_PROCESS = int(os.getenv('MAX_URLS_TO_PROCESS', '10'))

# Timeout for each URL scraping (seconds)
SCRAPING_TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', '30'))

# Generate image if not found in page
GENERATE_IMAGE_IF_NOT_FOUND = os.getenv('GENERATE_IMAGE_IF_NOT_FOUND', 'true').lower() == 'true'

# ============================================
# Logging Configuration
# ============================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'agent.log')

# ============================================
# Validation
# ============================================

def validate_config():
    """
    Validate that all required configuration variables are set.

    Raises:
        ValueError: If any required configuration is missing
    """
    required_vars = {
        'OPENAI_API_KEY': OPENAI_API_KEY,
        'TELEGRAM_API_ID': TELEGRAM_API_ID,
        'TELEGRAM_API_HASH': TELEGRAM_API_HASH,
        'TELEGRAM_PHONE': TELEGRAM_PHONE,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        raise ValueError(
            f"Missing required configuration variables: {', '.join(missing_vars)}\n"
            f"Please set them in your .env file or environment."
        )

    print("✓ Configuration validated successfully")


def print_config():
    """
    Print current configuration (hiding sensitive data).
    """
    print("\n" + "="*50)
    print("Agent Configuration")
    print("="*50)
    print(f"OpenAI Model: {OPENAI_MODEL}")
    print(f"OpenAI Image Model: {OPENAI_IMAGE_MODEL}")
    print(f"OpenAI API Key: {'*' * 20}{'...' if OPENAI_API_KEY else 'NOT SET'}")
    print(f"\nTelegram API ID: {TELEGRAM_API_ID or 'NOT SET'}")
    print(f"Telegram Phone: {TELEGRAM_PHONE or 'NOT SET'}")
    print(f"Telegram Chat ID: {TELEGRAM_CHAT_ID or 'NOT SET'}")
    print(f"\nFlask API URL: {FLASK_API_URL}")
    print(f"Headless Browser: {HEADLESS}")
    print(f"Browser Timeout: {BROWSER_TIMEOUT}ms")
    print(f"\nMax Messages: {MAX_MESSAGES_TO_PROCESS}")
    print(f"Max URLs: {MAX_URLS_TO_PROCESS}")
    print(f"Generate Images: {GENERATE_IMAGE_IF_NOT_FOUND}")
    print(f"\nLog Level: {LOG_LEVEL}")
    print("="*50 + "\n")


if __name__ == '__main__':
    # Test configuration
    try:
        validate_config()
        print_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
