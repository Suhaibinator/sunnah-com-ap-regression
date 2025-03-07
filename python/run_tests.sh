#!/bin/bash

# Script to run the Sunnah.com API regression tests

# Check if .env file exists in the project root
if [ ! -f "../.env" ]; then
    echo "Warning: .env file not found in the project root directory."
    echo "API keys will use default values. Create a .env file with API1_KEY and API2_KEY if needed."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txtp

# Create output directory if it doesn't exist
mkdir -p output

# Verify python-dotenv is installed
if ! pip list | grep -q "python-dotenv"; then
    echo "Warning: python-dotenv is not installed. Installing now..."
    pip install python-dotenv
fi

# Run tests
echo "Running API regression tests..."
python main.py "$@"

# Get exit code
EXIT_CODE=$?

# Open report if tests completed successfully
if [ -f "output/report.html" ]; then
    echo "Opening HTML report..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open output/report.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open output/report.html
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        start output/report.html
    else
        echo "Could not automatically open the report. Please open output/report.html manually."
    fi
fi

# Deactivate virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Done!"
exit $EXIT_CODE
