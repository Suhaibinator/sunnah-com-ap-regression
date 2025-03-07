# Sunnah.com API Regression Test Suite

This project provides a comprehensive regression test suite for comparing two different implementations of the Sunnah.com API. It uses the [Karate](https://github.com/intuit/karate) framework to perform API testing and comparison.

## Overview

The test suite follows a depth-first search approach to test all endpoints in the Sunnah.com API:

1. Get all collections
2. For each collection, get all books
3. For each book, get all chapters
4. For each book, get all hadiths
5. For specific hadiths, test individual hadith endpoints
6. Test random hadith endpoint

The tests compare responses from two different API implementations to ensure they return the same data.

## Project Structure

```
src/
├── test/
    ├── java/
    │   └── sunnah/
    │       └── api/
    │           └── ApiRegressionTest.java  # Test runner
    └── resources/
        ├── logback.xml                     # Logging configuration
        ├── karate-config.js                # Karate configuration
        └── sunnah/
            └── api/
                ├── common.feature          # Common functions
                ├── collections.feature     # Tests for collection endpoints
                ├── books.feature           # Tests for book endpoints
                └── hadiths.feature         # Tests for hadith endpoints
```

## Configuration

There are multiple ways to configure the API endpoints and API keys:

### Using a .env File (Recommended)

Create a `.env` file in the project root with the following content:

```
API1_KEY=your-api-key-1
API2_KEY=your-api-key-2
```

Replace `your-api-key-1` and `your-api-key-2` with your actual API keys. The `.env` file is automatically ignored by Git to keep your API keys secure.

### Using karate-config.js

You can also configure the API endpoints and API keys directly in `src/test/resources/karate-config.js`:

```javascript
var config = {
  env: env,
  // Define the two API implementations to compare
  apiImpl1: {
    baseUrl: 'https://api1.sunnah.com/v1',
    apiKey: 'your-api-key-1'
  },
  apiImpl2: {
    baseUrl: 'https://api2.sunnah.com/v1',
    apiKey: 'your-api-key-2'
  },
  // ...
};
```

Replace `'https://api1.sunnah.com/v1'`, `'https://api2.sunnah.com/v1'`, `'your-api-key-1'`, and `'your-api-key-2'` with the actual URLs and API keys for the two implementations you want to compare.

Note: If both a `.env` file and command-line arguments are provided, the command-line arguments will take precedence.

## Running the Tests

### Using the run-tests.sh Script

The project includes a convenient shell script for running tests with different configurations:

```bash
# Run all tests with default configuration
./run-tests.sh

# Run with custom API endpoints and keys
./run-tests.sh --api1-url https://api1.example.com/v1 --api2-url https://api2.example.com/v1 --api1-key your-key-1 --api2-key your-key-2

# Run a specific feature file
./run-tests.sh --feature collections.feature

# Show help
./run-tests.sh --help
```

### Using Gradle Directly

To run all tests:

```bash
./gradlew test
```

To run a specific feature file:

```bash
./gradlew karateExecute -Dkarate.options="classpath:sunnah/api/collections.feature"
```

### Verifying Setup

To verify that your setup is working correctly without making actual API calls, run:

```bash
./gradlew karateExecute -Dkarate.options="classpath:sunnah/api/setup-verification.feature"
```

## Test Reports

After running the tests, HTML reports will be generated in the `target/cucumber-html-reports` directory. Open `target/cucumber-html-reports/overview-features.html` in a browser to view the test results.

## How It Works

1. The tests first call the `/collections` endpoint to get a list of all collections.
2. For each collection, it tests the collection-specific endpoints and retrieves the books.
3. For each book, it tests the book-specific endpoints and retrieves the chapters and hadiths.
4. For each hadith, it tests the hadith-specific endpoints.
5. It also tests the random hadith endpoint.

For each endpoint, the test:
1. Makes a request to both API implementations
2. Compares the responses
3. Logs any differences found
4. Fails the test if the responses don't match

## Extending the Tests

To add tests for new endpoints:
1. Add the endpoint to the appropriate feature file
2. Follow the pattern of existing tests
3. Use the `compareApiResponses` function to compare responses from both implementations

## Troubleshooting

If you encounter issues:

1. **Dependency Compatibility**: If you encounter `NoSuchMethodError` or similar errors, try using a different version of Karate. You can update the version in `build.gradle`:
   ```gradle
   dependencies {
       testImplementation "com.intuit.karate:karate-junit5:1.1.0" // Try different versions: 1.0.0, 1.1.0, 1.2.0, etc.
       // Other dependencies...
   }
   ```

2. **API Keys**: Ensure you have valid API keys for both API implementations in `karate-config.js`

3. **Logs**: Check the logs in `build/reports/tests/test/index.html` for detailed error information

4. **Java Version**: Karate works best with Java 11 or higher. Check your Java version with `java -version`

5. **Clean Build**: Try cleaning your project before building:
   ```bash
   ./gradlew clean test
   ```
