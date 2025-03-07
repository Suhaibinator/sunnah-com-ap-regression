"""
Test script for the rate limiting backoff mechanism.
"""

import time
import logging
from api_client import ApiClient, ApiResponse
from config import API_IMPL1

# Set up logging to see the output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def simulate_rate_limit_response(client, endpoint, params=None):
    """
    Simulate a rate limited response by mocking the get method.
    """
    print(f"Testing rate limit backoff for endpoint: {endpoint}")
    
    # Store the original get method
    original_get = client.session.get
    
    # Counter for tracking calls
    call_count = 0
    
    # Mock the get method to return a 429 response
    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        # Create a mock response object
        class MockResponse:
            def __init__(self):
                self.status_code = 429
                self.text = '{"error": "Rate limit exceeded"}'
                self.headers = {"Retry-After": "2"}
            
            def json(self):
                return {"error": "Rate limit exceeded"}
        
        # After 3 calls, return a successful response
        if call_count > 2:
            print(f"Returning success response after {call_count} attempts")
            mock_resp = MockResponse()
            mock_resp.status_code = 200
            mock_resp.text = '{"data": "success"}'
            
            # Override the json method for the success response
            def success_json():
                return {"data": "success"}
            
            mock_resp.json = success_json
            return mock_resp
        
        print(f"Returning rate limit response (attempt {call_count})")
        return MockResponse()
    
    try:
        # Replace the get method with our mock
        client.session.get = mock_get
        
        # Call the get method which should now use our mock
        start_time = time.time()
        response = client.get(endpoint, params)
        end_time = time.time()
        
        # Print the results
        print(f"Total time: {end_time - start_time:.2f} seconds")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.body}")
        
        return response
    finally:
        # Restore the original get method
        client.session.get = original_get

def main():
    """
    Main function to run the test.
    """
    print("Testing rate limiting backoff mechanism...")
    
    # Create an API client
    client = ApiClient(API_IMPL1['base_url'], API_IMPL1['api_key'])
    
    # Test with a simulated rate limit response
    response = simulate_rate_limit_response(client, "collections")
    
    print("Test completed.")

if __name__ == "__main__":
    main()
