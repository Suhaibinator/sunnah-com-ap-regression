"""
Configuration settings for the Sunnah.com API regression testing.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env file in the project root (one directory up from the python directory)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# API Implementation 1 (Original)
API_IMPL1 = {
    'base_url': 'https://api.sunnah.com/v1',
    'api_key': os.getenv('API1_KEY', '')  # Get from .env or use empty string as fallback
}

# API Implementation 2 (New)
API_IMPL2 = {
    'base_url': 'http://localhost:8084/v1',
    'api_key': os.getenv('API2_KEY', 'your-api-key-2')  # Get from .env or use default as fallback
}

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Maximum number of retries for failed requests
MAX_RETRIES = 3

# Delay between retries in seconds (for non-rate-limited errors)
RETRY_DELAY = 1

# Exponential backoff settings for rate limiting
INITIAL_BACKOFF = 1  # Initial backoff time in seconds
MAX_BACKOFF = 60     # Maximum backoff time in seconds
BACKOFF_FACTOR = 2   # Multiplicative factor for exponential backoff

# Delay between consecutive API requests (in seconds) to avoid hitting rate limits
REQUEST_DELAY = 0.5

# Maximum number of concurrent requests
MAX_CONCURRENT_REQUESTS = 5

# Output directory for test results and data
OUTPUT_DIR = 'output'

# Pagination settings
DEFAULT_LIMIT = 50
MAX_LIMIT = 100

# Test settings
TEST_ALL_PAGES = True  # Set to True to test all pages of paginated endpoints
SAMPLE_SIZE = 5  # Number of items to sample from each collection/book for detailed testing
