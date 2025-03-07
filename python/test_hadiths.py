"""
Tests for the hadiths endpoints.
"""

import logging
import random
from typing import Dict, Any, List, Tuple

from api_client import ApiComparisonClient
from response_comparator import compare_responses, format_comparison_for_report
from data_store import (
    load_collections, load_books, load_hadiths,
    save_urns, load_urns, append_urn
)
from config import SAMPLE_SIZE

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_hadiths')


def test_hadith_by_number(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /collections/{collectionName}/hadiths/{hadithNumber} endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    # Load collections from previous tests
    collections = load_collections()
    
    if not collections:
        logger.warning("No collections found for testing GET /collections/{collectionName}/hadiths/{hadithNumber}")
        return
    
    for collection in collections:
        collection_name = collection.get('name')
        if not collection_name:
            logger.warning("Collection missing 'name' field, skipping")
            continue
        
        # Load books for this collection
        books = load_books(collection_name)
        
        if not books:
            logger.warning(f"No books found for collection {collection_name}")
            continue
        
        # Test a sample of books
        sample = books[:SAMPLE_SIZE] if len(books) > SAMPLE_SIZE else books
        
        for book in sample:
            book_number = book.get('bookNumber')
            if not book_number:
                logger.warning("Book missing 'bookNumber' field, skipping")
                continue
            
            # Load hadiths for this book
            hadiths = load_hadiths(collection_name, book_number)
            
            if not hadiths:
                logger.warning(f"No hadiths found for collection {collection_name}, book {book_number}")
                continue
            
            # Test a sample of hadiths
            hadith_sample = hadiths[:SAMPLE_SIZE] if len(hadiths) > SAMPLE_SIZE else hadiths
            
            for hadith in hadith_sample:
                hadith_number = hadith.get('hadithNumber')
                if not hadith_number:
                    logger.warning("Hadith missing 'hadithNumber' field, skipping")
                    continue
                
                logger.info(f"Testing GET /collections/{collection_name}/hadiths/{hadith_number}")
                
                # Test the endpoint
                endpoint = f'collections/{collection_name}/hadiths/{hadith_number}'
                response1, response2 = client.compare_get(endpoint)
                
                # Compare responses
                result = compare_responses(response1, response2, endpoint)
                results.append(format_comparison_for_report(result))
                
                # Extract and save URNs for further testing
                if response1.is_success() and response1.body and 'hadith' in response1.body:
                    for hadith_lang in response1.body['hadith']:
                        if 'urn' in hadith_lang:
                            append_urn(hadith_lang['urn'])
                            logger.info(f"Saved URN {hadith_lang['urn']} for further testing")


def test_hadith_by_urn(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /hadiths/{urn} endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    # Load URNs from previous tests
    urns = load_urns()
    
    if not urns:
        logger.warning("No URNs found for testing GET /hadiths/{urn}")
        return
    
    # Test a sample of URNs
    sample = urns[:SAMPLE_SIZE] if len(urns) > SAMPLE_SIZE else urns
    
    for urn in sample:
        logger.info(f"Testing GET /hadiths/{urn}")
        
        # Test the endpoint
        endpoint = f'hadiths/{urn}'
        response1, response2 = client.compare_get(endpoint)
        
        # Compare responses
        result = compare_responses(response1, response2, endpoint)
        results.append(format_comparison_for_report(result))


def test_random_hadith(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /hadiths/random endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    logger.info("Testing GET /hadiths/random")
    
    # Test the endpoint multiple times to ensure randomness
    for i in range(3):
        logger.info(f"Random hadith test {i+1}/3")
        
        # Test the endpoint
        endpoint = 'hadiths/random'
        response1, response2 = client.compare_get(endpoint)
        
        # For random hadiths, we don't compare the actual content since they're random
        # We just check that both APIs return valid responses
        if response1.is_success() and response2.is_success():
            logger.info("✅ Both APIs returned successful responses for random hadith")
            results.append({
                'endpoint': endpoint,
                'params': 'None',
                'status': 'PASS',
                'differences': []
            })
        else:
            logger.error("❌ API response failure for random hadith")
            differences = []
            
            if not response1.is_success():
                differences.append(f"API1 error: {response1.status_code}")
            
            if not response2.is_success():
                differences.append(f"API2 error: {response2.status_code}")
            
            results.append({
                'endpoint': endpoint,
                'params': 'None',
                'status': 'FAIL',
                'differences': differences
            })
        
        # Extract and save URNs for further testing
        if response1.is_success() and response1.body and 'hadith' in response1.body:
            for hadith_lang in response1.body['hadith']:
                if 'urn' in hadith_lang:
                    append_urn(hadith_lang['urn'])
                    logger.info(f"Saved URN {hadith_lang['urn']} from random hadith for further testing")


def run_hadiths_tests() -> List[Dict[str, Any]]:
    """
    Run all tests for the hadiths endpoints.
    
    Returns:
        List of test results
    """
    logger.info("Running hadiths tests")
    
    client = ApiComparisonClient()
    results = []
    
    # Test GET /collections/{collectionName}/hadiths/{hadithNumber}
    test_hadith_by_number(client, results)
    
    # Test GET /hadiths/{urn}
    test_hadith_by_urn(client, results)
    
    # Test GET /hadiths/random
    test_random_hadith(client, results)
    
    logger.info(f"Completed hadiths tests: {len(results)} tests run")
    return results


if __name__ == '__main__':
    # Run tests if this file is executed directly
    run_hadiths_tests()
