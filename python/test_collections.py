"""
Tests for the collections endpoints.
"""

import logging
from typing import Dict, Any, List, Tuple

from api_client import ApiComparisonClient
from response_comparator import compare_responses, compare_paginated_responses, format_comparison_for_report
from data_store import save_collections, load_collections
from config import TEST_ALL_PAGES, DEFAULT_LIMIT

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_collections')


def test_collections_list(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /collections endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    logger.info("Testing GET /collections")
    
    # Test with default parameters
    response1, response2 = client.compare_get('collections')
    
    # Compare responses
    result = compare_paginated_responses(response1, response2, 'collections')
    results.append(format_comparison_for_report(result))
    
    # Save collections for further testing if successful
    if response1.is_success() and response1.body and 'data' in response1.body:
        collections = response1.body['data']
        save_collections(collections)
        logger.info(f"Saved {len(collections)} collections for further testing")
    
    # Test pagination if enabled
    if TEST_ALL_PAGES and response1.is_success() and response1.body and 'total' in response1.body:
        total = response1.body['total']
        pages = (total + DEFAULT_LIMIT - 1) // DEFAULT_LIMIT
        
        for page in range(2, pages + 1):
            logger.info(f"Testing GET /collections page {page}/{pages}")
            
            # Test with pagination parameters
            params = {'page': page, 'limit': DEFAULT_LIMIT}
            response1, response2 = client.compare_get('collections', params)
            
            # Compare responses
            result = compare_paginated_responses(response1, response2, 'collections', params)
            results.append(format_comparison_for_report(result))


def test_collection_by_name(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /collections/{collectionName} endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    # Load collections from previous tests
    collections = load_collections()
    
    if not collections:
        logger.warning("No collections found for testing GET /collections/{collectionName}")
        return
    
    for collection in collections:
        collection_name = collection.get('name')
        if not collection_name:
            logger.warning("Collection missing 'name' field, skipping")
            continue
        
        logger.info(f"Testing GET /collections/{collection_name}")
        
        # Test the endpoint
        response1, response2 = client.compare_get(f'collections/{collection_name}')
        
        # Compare responses
        result = compare_responses(response1, response2, f'collections/{collection_name}')
        results.append(format_comparison_for_report(result))


def run_collections_tests() -> List[Dict[str, Any]]:
    """
    Run all tests for the collections endpoints.
    
    Returns:
        List of test results
    """
    logger.info("Running collections tests")
    
    client = ApiComparisonClient()
    results = []
    
    # Test GET /collections
    test_collections_list(client, results)
    
    # Test GET /collections/{collectionName}
    test_collection_by_name(client, results)
    
    logger.info(f"Completed collections tests: {len(results)} tests run")
    return results


if __name__ == '__main__':
    # Run tests if this file is executed directly
    run_collections_tests()
