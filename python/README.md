# Sunnah.com API Regression Testing

This project provides a comprehensive API testing framework for comparing two implementations of the Sunnah.com API:

1. The original API at `https://api.sunnah.com/v1`
2. The new implementation at `http://localhost:8084/v1`

The framework tests all endpoints defined in the OpenAPI specification, comparing the responses from both implementations to ensure they match.

## Features

- Tests all endpoints in the Sunnah.com API
- Compares responses from two API implementations using semantic JSON comparison
- Tests pagination for all paginated endpoints
- Generates detailed HTML and JSON reports
- Configurable test parameters (sample size, pagination, etc.)
- Comprehensive logging

## Requirements

- Python 3.6+
- Required Python packages (installed automatically by the run script):
  - requests
  - pytest
  - pytest-html
  - deepdiff
  - jsonschema

## Configuration

Configuration settings are defined in `config.py`:

- API endpoints and keys
- Request timeout and retry settings
- Rate limiting backoff settings
- Output directory for test results
- Pagination settings
- Test settings (sample size, etc.)

### Environment Variables

The API keys can be configured using environment variables or a `.env` file in the project root directory. The framework uses the `python-dotenv` library to load environment variables from the `.env` file.

Create a `.env` file in the project root directory (one level up from the `python` directory) with the following content:

```
API1_KEY=your-api1-key
API2_KEY=your-api2-key
```

If the `.env` file is not found or the environment variables are not set, the framework will use the default values defined in `config.py`.

## Running the Tests

### Using the Run Script

The easiest way to run the tests is using the provided shell script:

```bash
cd python
./run_tests.sh
```

This script will:
1. Create a virtual environment if it doesn't exist
2. Install the required dependencies
3. Run the tests
4. Open the HTML report when tests complete

### Command Line Options

You can pass command line options to the test runner:

```bash
./run_tests.sh --collections-only  # Run only collections tests
./run_tests.sh --books-only        # Run only books tests
./run_tests.sh --hadiths-only      # Run only hadiths tests
./run_tests.sh --no-report         # Do not generate HTML and JSON reports
```

### Running Manually

If you prefer to run the tests manually:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python main.py
```

## Rate Limiting Backoff

The API client includes a sophisticated rate limiting backoff mechanism to handle API rate limits gracefully:

- **Exponential Backoff**: When a rate limit (HTTP 429) is encountered, the client uses exponential backoff with jitter to wait before retrying.
- **Retry-After Header Support**: If the API provides a `Retry-After` header, the client respects this value for the wait time.
- **Configurable Parameters**: The backoff behavior can be configured through the following parameters in `config.py`:
  - `INITIAL_BACKOFF`: Starting backoff time in seconds (default: 1)
  - `MAX_BACKOFF`: Maximum backoff time in seconds (default: 60)
  - `BACKOFF_FACTOR`: Multiplicative factor for exponential backoff (default: 2)
  - `REQUEST_DELAY`: Delay between consecutive API requests to avoid hitting rate limits (default: 0.5)

This ensures that the tests can run reliably even when API rate limits are encountered, and prevents the tests from overwhelming the API with too many requests in a short period.

## Project Structure

- `config.py`: Configuration settings
- `api_client.py`: Client for making API requests with rate limiting backoff
- `response_comparator.py`: Utility for comparing API responses
- `data_store.py`: Data store for saving and retrieving data between test runs
- `test_collections.py`: Tests for collection endpoints
- `test_books.py`: Tests for book endpoints
- `test_hadiths.py`: Tests for hadith endpoints
- `report_generator.py`: Generate HTML and JSON reports
- `main.py`: Main script to run all tests
- `run_tests.sh`: Shell script to run tests

## Test Flow

1. Test collections endpoints and save collection data
2. Test books endpoints for each collection and save book data
3. Test chapters endpoints for each book and save chapter data
4. Test hadiths endpoints for each book and save hadith data
5. Test individual hadith endpoints using saved data
6. Test hadith URN endpoints using extracted URNs
7. Test random hadith endpoint
8. Generate reports

## Reports

After running the tests, reports are generated in the `output` directory:

- `report.html`: HTML report with detailed test results
- `report.json`: JSON report with test results
- `test_run.log`: Log file with detailed test execution information

The HTML report provides a summary of test results and detailed information about any differences found between the API implementations.
