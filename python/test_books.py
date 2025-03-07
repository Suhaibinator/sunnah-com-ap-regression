"""
Tests for the books endpoints.
"""

import logging
from typing import Dict, Any, List, Tuple

from api_client import ApiComparisonClient
from response_comparator import compare_responses, compare_paginated_responses, format_comparison_for_report
from data_store import (
    load_collections, save_books, load_books,
    save_chapters, load_chapters, save_hadiths, load_hadiths
)
from config import TEST_ALL_PAGES, DEFAULT_LIMIT, SAMPLE_SIZE

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_books')


def test_books_list(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /collections/{collectionName}/books endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    # Load collections from previous tests
    collections = load_collections()
    
    if not collections:
        logger.warning("No collections found for testing GET /collections/{collectionName}/books")
        return
    
    for collection in collections:
        collection_name = collection.get('name')
        if not collection_name:
            logger.warning("Collection missing 'name' field, skipping")
            continue
        
        # Skip collections that don't have books
        if not collection.get('hasBooks', True):
            logger.info(f"Collection {collection_name} doesn't have books, skipping")
            continue
        
        logger.info(f"Testing GET /collections/{collection_name}/books")
        
        # Test with default parameters
        endpoint = f'collections/{collection_name}/books'
        response1, response2 = client.compare_get(endpoint)
        
        # Compare responses
        result = compare_paginated_responses(response1, response2, endpoint)
        results.append(format_comparison_for_report(result))
        
        # Save books for further testing if successful
        if response1.is_success() and response1.body and 'data' in response1.body:
            books = response1.body['data']
            save_books(collection_name, books)
            logger.info(f"Saved {len(books)} books for collection {collection_name}")
        
        # Test pagination if enabled
        if TEST_ALL_PAGES and response1.is_success() and response1.body and 'total' in response1.body:
            total = response1.body['total']
            pages = (total + DEFAULT_LIMIT - 1) // DEFAULT_LIMIT
            
            for page in range(2, pages + 1):
                logger.info(f"Testing GET /collections/{collection_name}/books page {page}/{pages}")
                
                # Test with pagination parameters
                params = {'page': page, 'limit': DEFAULT_LIMIT}
                response1, response2 = client.compare_get(endpoint, params)
                
                # Compare responses
                result = compare_paginated_responses(response1, response2, endpoint, params)
                results.append(format_comparison_for_report(result))


def test_book_by_number(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /collections/{collectionName}/books/{bookNumber} endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    # Load collections from previous tests
    collections = load_collections()
    
    if not collections:
        logger.warning("No collections found for testing GET /collections/{collectionName}/books/{bookNumber}")
        return
    
    for collection in collections:
        collection_name = collection.get('name')
        if not collection_name:
            logger.warning("Collection missing 'name' field, skipping")
            continue
        
        # Skip collections that don't have books
        if not collection.get('hasBooks', True):
            logger.info(f"Collection {collection_name} doesn't have books, skipping")
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
            
            logger.info(f"Testing GET /collections/{collection_name}/books/{book_number}")
            
            # Test the endpoint
            endpoint = f'collections/{collection_name}/books/{book_number}'
            response1, response2 = client.compare_get(endpoint)
            
            # Compare responses
            result = compare_responses(response1, response2, endpoint)
            results.append(format_comparison_for_report(result))


def test_chapters_list(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /collections/{collectionName}/books/{bookNumber}/chapters endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    # Load collections from previous tests
    collections = load_collections()
    
    if not collections:
        logger.warning("No collections found for testing GET /collections/{collectionName}/books/{bookNumber}/chapters")
        return
    
    for collection in collections:
        collection_name = collection.get('name')
        if not collection_name:
            logger.warning("Collection missing 'name' field, skipping")
            continue
        
        # Skip collections that don't have books or chapters
        if not collection.get('hasBooks', True) or not collection.get('hasChapters', True):
            logger.info(f"Collection {collection_name} doesn't have books or chapters, skipping")
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
            
            logger.info(f"Testing GET /collections/{collection_name}/books/{book_number}/chapters")
            
            # Test with default parameters
            endpoint = f'collections/{collection_name}/books/{book_number}/chapters'
            response1, response2 = client.compare_get(endpoint)
            
            # Compare responses
            result = compare_paginated_responses(response1, response2, endpoint)
            results.append(format_comparison_for_report(result))
            
            # Save chapters for further testing if successful
            if response1.is_success() and response1.body and 'data' in response1.body:
                chapters = response1.body['data']
                save_chapters(collection_name, book_number, chapters)
                logger.info(f"Saved {len(chapters)} chapters for collection {collection_name}, book {book_number}")
            
            # Test pagination if enabled
            if TEST_ALL_PAGES and response1.is_success() and response1.body and 'total' in response1.body:
                total = response1.body['total']
                pages = (total + DEFAULT_LIMIT - 1) // DEFAULT_LIMIT
                
                for page in range(2, pages + 1):
                    logger.info(f"Testing GET /collections/{collection_name}/books/{book_number}/chapters page {page}/{pages}")
                    
                    # Test with pagination parameters
                    params = {'page': page, 'limit': DEFAULT_LIMIT}
                    response1, response2 = client.compare_get(endpoint, params)
                    
                    # Compare responses
                    result = compare_paginated_responses(response1, response2, endpoint, params)
                    results.append(format_comparison_for_report(result))


def test_chapter_by_id(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /collections/{collectionName}/books/{bookNumber}/chapters/{chapterId} endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    # Load collections from previous tests
    collections = load_collections()
    
    if not collections:
        logger.warning("No collections found for testing GET /collections/{collectionName}/books/{bookNumber}/chapters/{chapterId}")
        return
    
    for collection in collections:
        collection_name = collection.get('name')
        if not collection_name:
            logger.warning("Collection missing 'name' field, skipping")
            continue
        
        # Skip collections that don't have books or chapters
        if not collection.get('hasBooks', True) or not collection.get('hasChapters', True):
            logger.info(f"Collection {collection_name} doesn't have books or chapters, skipping")
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
            
            # Load chapters for this book
            chapters = load_chapters(collection_name, book_number)
            
            if not chapters:
                logger.warning(f"No chapters found for collection {collection_name}, book {book_number}")
                continue
            
            # Test a sample of chapters
            chapter_sample = chapters[:SAMPLE_SIZE] if len(chapters) > SAMPLE_SIZE else chapters
            
            for chapter in chapter_sample:
                chapter_id = chapter.get('chapterId')
                if not chapter_id:
                    logger.warning("Chapter missing 'chapterId' field, skipping")
                    continue
                
                logger.info(f"Testing GET /collections/{collection_name}/books/{book_number}/chapters/{chapter_id}")
                
                # Test the endpoint
                endpoint = f'collections/{collection_name}/books/{book_number}/chapters/{chapter_id}'
                response1, response2 = client.compare_get(endpoint)
                
                # Compare responses
                result = compare_responses(response1, response2, endpoint)
                results.append(format_comparison_for_report(result))


def test_hadiths_list(client: ApiComparisonClient, results: List[Dict[str, Any]]) -> None:
    """
    Test the GET /collections/{collectionName}/books/{bookNumber}/hadiths endpoint.
    
    Args:
        client: The API comparison client
        results: List to append test results to
    """
    # Load collections from previous tests
    collections = load_collections()
    
    if not collections:
        logger.warning("No collections found for testing GET /collections/{collectionName}/books/{bookNumber}/hadiths")
        return
    
    for collection in collections:
        collection_name = collection.get('name')
        if not collection_name:
            logger.warning("Collection missing 'name' field, skipping")
            continue
        
        # Skip collections that don't have books
        if not collection.get('hasBooks', True):
            logger.info(f"Collection {collection_name} doesn't have books, skipping")
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
            
            logger.info(f"Testing GET /collections/{collection_name}/books/{book_number}/hadiths")
            
            # Test with default parameters
            endpoint = f'collections/{collection_name}/books/{book_number}/hadiths'
            response1, response2 = client.compare_get(endpoint)
            
            # Compare responses
            result = compare_paginated_responses(response1, response2, endpoint)
            results.append(format_comparison_for_report(result))
            
            # Save hadiths for further testing if successful
            if response1.is_success() and response1.body and 'data' in response1.body:
                hadiths = response1.body['data']
                save_hadiths(collection_name, book_number, hadiths)
                logger.info(f"Saved {len(hadiths)} hadiths for collection {collection_name}, book {book_number}")
            
            # Test pagination if enabled
            if TEST_ALL_PAGES and response1.is_success() and response1.body and 'total' in response1.body:
                total = response1.body['total']
                pages = (total + DEFAULT_LIMIT - 1) // DEFAULT_LIMIT
                
                for page in range(2, pages + 1):
                    logger.info(f"Testing GET /collections/{collection_name}/books/{book_number}/hadiths page {page}/{pages}")
                    
                    # Test with pagination parameters
                    params = {'page': page, 'limit': DEFAULT_LIMIT}
                    response1, response2 = client.compare_get(endpoint, params)
                    
                    # Compare responses
                    result = compare_paginated_responses(response1, response2, endpoint, params)
                    results.append(format_comparison_for_report(result))


def run_books_tests() -> List[Dict[str, Any]]:
    """
    Run all tests for the books endpoints.
    
    Returns:
        List of test results
    """
    logger.info("Running books tests")
    
    client = ApiComparisonClient()
    results = []
    
    # Test GET /collections/{collectionName}/books
    test_books_list(client, results)
    
    # Test GET /collections/{collectionName}/books/{bookNumber}
    test_book_by_number(client, results)
    
    # Test GET /collections/{collectionName}/books/{bookNumber}/chapters
    test_chapters_list(client, results)
    
    # Test GET /collections/{collectionName}/books/{bookNumber}/chapters/{chapterId}
    test_chapter_by_id(client, results)
    
    # Test GET /collections/{collectionName}/books/{bookNumber}/hadiths
    test_hadiths_list(client, results)
    
    logger.info(f"Completed books tests: {len(results)} tests run")
    return results


if __name__ == '__main__':
    # Run tests if this file is executed directly
    run_books_tests()
