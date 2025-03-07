"""
API client for making requests to the Sunnah.com API implementations.
"""

import os
import time
import json
import logging
import random
from typing import Dict, Any, Optional, Tuple, List

import requests
from requests.exceptions import RequestException

from config import (
    API_IMPL1, API_IMPL2, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY, OUTPUT_DIR,
    INITIAL_BACKOFF, MAX_BACKOFF, BACKOFF_FACTOR, REQUEST_DELAY
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_client')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


class ApiResponse:
    """Class to represent an API response with status code and body."""
    
    def __init__(self, status_code: int, body: Any, headers: Dict[str, str] = None, error: str = None):
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}
        self.error = error
    
    def is_success(self) -> bool:
        """Check if the response was successful (status code 2xx)."""
        return 200 <= self.status_code < 300
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary."""
        return {
            'status_code': self.status_code,
            'body': self.body,
            'headers': self.headers,
            'error': self.error
        }
    
    def __str__(self) -> str:
        """String representation of the response."""
        return f"ApiResponse(status_code={self.status_code}, error={self.error})"


class ApiClient:
    """Client for making requests to the Sunnah.com API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Accept': 'application/json'
        })
    
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> ApiResponse:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: The API endpoint (without the base URL)
            params: Query parameters to include in the request
            
        Returns:
            ApiResponse object containing the response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"Making GET request to {url}")
        
        backoff_time = INITIAL_BACKOFF
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=REQUEST_TIMEOUT
                )
                
                # Try to parse JSON response
                try:
                    body = response.json() if response.text else None
                except ValueError:
                    body = response.text
                
                # Check if we're being rate limited
                if response.status_code == 429:
                    # Get retry-after header if available
                    retry_after = response.headers.get('Retry-After')
                    
                    if retry_after and retry_after.isdigit():
                        # If Retry-After header is present and is a number, use it
                        wait_time = int(retry_after)
                    else:
                        # Otherwise use exponential backoff with jitter
                        wait_time = min(backoff_time + random.uniform(0, 1), MAX_BACKOFF)
                        backoff_time *= BACKOFF_FACTOR
                    
                    logger.warning(f"Rate limited (attempt {attempt + 1}/{MAX_RETRIES}). Waiting {wait_time:.2f} seconds before retry.")
                    time.sleep(wait_time)
                    continue
                
                # Return response for non-rate-limit errors or successful responses
                return ApiResponse(
                    status_code=response.status_code,
                    body=body,
                    headers=dict(response.headers)
                )
            
            except RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    # Use exponential backoff with jitter for network errors too
                    wait_time = min(backoff_time + random.uniform(0, 1), MAX_BACKOFF)
                    logger.info(f"Waiting {wait_time:.2f} seconds before retry.")
                    time.sleep(wait_time)
                    backoff_time *= BACKOFF_FACTOR
                else:
                    return ApiResponse(
                        status_code=0,
                        body=None,
                        error=str(e)
                    )
        
        # If we've exhausted all retries and still getting rate limited
        return ApiResponse(
            status_code=429,
            body=None,
            error="Rate limit exceeded after maximum retries"
        )


class ApiComparisonClient:
    """Client for comparing responses from two API implementations."""
    
    def __init__(self):
        self.api1 = ApiClient(API_IMPL1['base_url'], API_IMPL1['api_key'])
        self.api2 = ApiClient(API_IMPL2['base_url'], API_IMPL2['api_key'])
    
    def compare_get(self, endpoint: str, params: Dict[str, Any] = None) -> Tuple[ApiResponse, ApiResponse]:
        """
        Make GET requests to both API implementations and return the responses.
        
        Args:
            endpoint: The API endpoint (without the base URL)
            params: Query parameters to include in the request
            
        Returns:
            Tuple of (api1_response, api2_response)
        """
        logger.info(f"Comparing GET {endpoint} with params {params}")
        
        # Make request to first API
        response1 = self.api1.get(endpoint, params)
        logger.info(f"API1 response: {response1.status_code}")
        
        # Add a delay between requests to avoid hitting rate limits
        # This is especially important if both APIs are actually the same server
        # but with different endpoints
        time.sleep(REQUEST_DELAY)
        
        # Make request to second API
        response2 = self.api2.get(endpoint, params)
        logger.info(f"API2 response: {response2.status_code}")
        
        return response1, response2
    
    def save_responses(self, endpoint: str, params: Dict[str, Any], 
                      response1: ApiResponse, response2: ApiResponse) -> None:
        """
        Save API responses to files for debugging and analysis.
        
        Args:
            endpoint: The API endpoint
            params: Query parameters
            response1: Response from API1
            response2: Response from API2
        """
        # Create a safe filename from the endpoint and params
        safe_endpoint = endpoint.replace('/', '_').strip('_')
        params_str = '_'.join(f"{k}_{v}" for k, v in (params or {}).items())
        filename = f"{safe_endpoint}_{params_str}" if params_str else safe_endpoint
        
        # Save responses
        with open(os.path.join(OUTPUT_DIR, f"{filename}_api1.json"), 'w') as f:
            json.dump(response1.to_dict(), f, indent=2)
        
        with open(os.path.join(OUTPUT_DIR, f"{filename}_api2.json"), 'w') as f:
            json.dump(response2.to_dict(), f, indent=2)


def extract_data_from_paginated_response(response: ApiResponse) -> List[Dict[str, Any]]:
    """
    Extract data items from a paginated API response.
    
    Args:
        response: The API response
        
    Returns:
        List of data items
    """
    if not response.is_success() or not response.body:
        return []
    
    # Check if the response has a 'data' field (paginated response)
    if isinstance(response.body, dict) and 'data' in response.body:
        return response.body['data']
    
    # If it's a single item response
    return [response.body] if isinstance(response.body, dict) else []


def get_all_pages(client: ApiClient, endpoint: str, 
                 base_params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Get all pages of a paginated API endpoint.
    
    Args:
        client: The API client
        endpoint: The API endpoint
        base_params: Base query parameters
        
    Returns:
        List of all data items across all pages
    """
    all_items = []
    page = 1
    has_more = True
    
    while has_more:
        params = {**(base_params or {}), 'page': page}
        response = client.get(endpoint, params)
        
        # If we got rate limited even after retries, log and break
        if response.status_code == 429:
            logger.error(f"Rate limit exceeded for page {page} of {endpoint} after maximum retries")
            break
        # For other errors, log and break
        elif not response.is_success():
            logger.error(f"Failed to get page {page} of {endpoint}: {response.error or response.status_code}")
            break
        
        # Extract data from the response
        items = extract_data_from_paginated_response(response)
        all_items.extend(items)
        
        # Check if there are more pages
        if isinstance(response.body, dict) and response.body.get('next'):
            page += 1
            # Add a delay between paginated requests to avoid hitting rate limits
            time.sleep(REQUEST_DELAY)
        else:
            has_more = False
    
    return all_items
