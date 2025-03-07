#!/bin/bash

# Script to run Sunnah.com API regression tests

# Default values
API1_URL="https://api.sunnah.com/v1"
API2_URL="http://localhost:8084/v1"
FEATURE_FILE=""

# Load values from .env file if it exists
if [ -f .env ]; then
  echo "Loading API keys from .env file..."
  while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [ -z "$line" ] || [[ "$line" =~ ^# ]]; then
      continue
    fi
    
    # Extract key and value
    key=$(echo "$line" | cut -d= -f1)
    value=$(echo "$line" | cut -d= -f2-)
    
    # Set variables based on keys
    if [ "$key" = "API1_KEY" ]; then
      API1_KEY="$value"
    elif [ "$key" = "API2_KEY" ]; then
      API2_KEY="$value"
    fi
  done < .env
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --api1-url)
      API1_URL="$2"
      shift 2
      ;;
    --api2-url)
      API2_URL="$2"
      shift 2
      ;;
    --api1-key)
      API1_KEY="$2"
      shift 2
      ;;
    --api2-key)
      API2_KEY="$2"
      shift 2
      ;;
    --feature)
      FEATURE_FILE="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --api1-url URL    URL for the first API implementation (default: $API1_URL)"
      echo "  --api2-url URL    URL for the second API implementation (default: $API2_URL)"
      echo "  --api1-key KEY    API key for the first API implementation"
      echo "  --api2-key KEY    API key for the second API implementation"
      echo "  --feature FILE    Run a specific feature file (e.g., collections.feature)"
      echo "  --help            Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Create a temporary karate-config.js with the provided values
TMP_CONFIG=$(mktemp)
cat > $TMP_CONFIG << EOF
function fn() {
  var env = karate.env;
  karate.log('karate.env =', env);
  if (!env) {
    env = 'dev';
  }
  
  var config = {
    env: env,
    apiImpl1: {
      baseUrl: '$API1_URL',
      apiKey: '$API1_KEY'
    },
    apiImpl2: {
      baseUrl: '$API2_URL',
      apiKey: '$API2_KEY'
    },
    compareResponses: function(response1, response2) {
      var result = {
        equal: true,
        differences: []
      };
      
      if (response1.status !== response2.status) {
        result.equal = false;
        result.differences.push('Status codes differ: ' + response1.status + ' vs ' + response2.status);
      }
      
      try {
        var body1 = response1.json;
        var body2 = response2.json;
        
        var diff = karate.match(body1, body2).error;
        if (diff) {
          result.equal = false;
          result.differences.push('Response bodies differ: ' + diff);
        }
      } catch (e) {
        result.equal = false;
        result.differences.push('Error comparing responses: ' + e);
      }
      
      return result;
    }
  };
  
  karate.configure('connectTimeout', 5000);
  karate.configure('readTimeout', 5000);
  
  return config;
}
EOF

# Copy the temporary config to the actual config file
cp $TMP_CONFIG src/test/resources/karate-config.js
rm $TMP_CONFIG

# Run the tests
if [ -n "$FEATURE_FILE" ]; then
  if [[ "$FEATURE_FILE" == *"-direct.feature" || "$FEATURE_FILE" == "api-test.feature" ]]; then
    echo "Running direct feature file: $FEATURE_FILE"
    ./gradlew test --tests "sunnah.api.DirectApiRegressionTest" -Dkarate.options="classpath:sunnah/api/$FEATURE_FILE"
  else
    echo "Running feature file: $FEATURE_FILE"
    ./gradlew test --tests "sunnah.api.ApiRegressionTest" -Dkarate.options="classpath:sunnah/api/$FEATURE_FILE"
  fi
else
  echo "Running direct tests (recommended)"
  ./gradlew test --tests "sunnah.api.DirectApiRegressionTest"
fi

# Open the test report
if [ -f "build/reports/tests/test/index.html" ]; then
  echo "Opening test report..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    open build/reports/tests/test/index.html
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open build/reports/tests/test/index.html
  elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    start build/reports/tests/test/index.html
  else
    echo "Test report available at: build/reports/tests/test/index.html"
  fi
else
  echo "Test report not found. Check for errors in the test execution."
fi
