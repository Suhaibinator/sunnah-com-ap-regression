"""
Data store for saving and retrieving data between test runs.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from config import OUTPUT_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_store')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_data(data: Any, filename: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save
        filename: The filename (without path)
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved data to {filepath}")
    except Exception as e:
        logger.error(f"Error saving data to {filepath}: {str(e)}")


def load_data(filename: str, default: Any = None) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        filename: The filename (without path)
        default: Default value to return if the file doesn't exist
        
    Returns:
        The loaded data or the default value
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded data from {filepath}")
            return data
        else:
            logger.warning(f"File {filepath} not found, returning default value")
            return default
    except Exception as e:
        logger.error(f"Error loading data from {filepath}: {str(e)}")
        return default


def save_collections(collections: List[Dict[str, Any]]) -> None:
    """
    Save collections data.
    
    Args:
        collections: List of collection objects
    """
    save_data(collections, 'collections.json')


def load_collections() -> List[Dict[str, Any]]:
    """
    Load collections data.
    
    Returns:
        List of collection objects
    """
    return load_data('collections.json', [])


def save_books(collection_name: str, books: List[Dict[str, Any]]) -> None:
    """
    Save books data for a collection.
    
    Args:
        collection_name: Name of the collection
        books: List of book objects
    """
    save_data(books, f'books_{collection_name}.json')


def load_books(collection_name: str) -> List[Dict[str, Any]]:
    """
    Load books data for a collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        List of book objects
    """
    return load_data(f'books_{collection_name}.json', [])


def save_chapters(collection_name: str, book_number: str, chapters: List[Dict[str, Any]]) -> None:
    """
    Save chapters data for a book.
    
    Args:
        collection_name: Name of the collection
        book_number: Number of the book
        chapters: List of chapter objects
    """
    save_data(chapters, f'chapters_{collection_name}_{book_number}.json')


def load_chapters(collection_name: str, book_number: str) -> List[Dict[str, Any]]:
    """
    Load chapters data for a book.
    
    Args:
        collection_name: Name of the collection
        book_number: Number of the book
        
    Returns:
        List of chapter objects
    """
    return load_data(f'chapters_{collection_name}_{book_number}.json', [])


def save_hadiths(collection_name: str, book_number: str, hadiths: List[Dict[str, Any]]) -> None:
    """
    Save hadiths data for a book.
    
    Args:
        collection_name: Name of the collection
        book_number: Number of the book
        hadiths: List of hadith objects
    """
    save_data(hadiths, f'hadiths_{collection_name}_{book_number}.json')


def load_hadiths(collection_name: str, book_number: str) -> List[Dict[str, Any]]:
    """
    Load hadiths data for a book.
    
    Args:
        collection_name: Name of the collection
        book_number: Number of the book
        
    Returns:
        List of hadith objects
    """
    return load_data(f'hadiths_{collection_name}_{book_number}.json', [])


def save_urns(urns: List[int]) -> None:
    """
    Save URNs data.
    
    Args:
        urns: List of URNs
    """
    save_data(urns, 'urns.json')


def load_urns() -> List[int]:
    """
    Load URNs data.
    
    Returns:
        List of URNs
    """
    return load_data('urns.json', [])


def append_urn(urn: int) -> None:
    """
    Append a URN to the URNs list.
    
    Args:
        urn: The URN to append
    """
    urns = load_urns()
    if urn not in urns:
        urns.append(urn)
        save_urns(urns)


def save_test_results(results: List[Dict[str, Any]]) -> None:
    """
    Save test results.
    
    Args:
        results: List of test result objects
    """
    save_data(results, 'test_results.json')


def load_test_results() -> List[Dict[str, Any]]:
    """
    Load test results.
    
    Returns:
        List of test result objects
    """
    return load_data('test_results.json', [])


def append_test_result(result: Dict[str, Any]) -> None:
    """
    Append a test result to the results list.
    
    Args:
        result: The test result to append
    """
    results = load_test_results()
    results.append(result)
    save_test_results(results)
    
    # If the test failed, also save it to the failed endpoints file
    if result.get('status') == 'FAIL':
        save_failed_endpoint(result)


def save_failed_endpoint(result: Dict[str, Any]) -> None:
    """
    Save a failed endpoint to the failed endpoints file.
    
    Args:
        result: The test result to save
    """
    filepath = os.path.join(OUTPUT_DIR, 'failed_endpoints.json')
    
    # Load existing failed endpoints
    failed_endpoints = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                failed_endpoints = json.load(f)
        except Exception as e:
            logger.error(f"Error loading failed endpoints from {filepath}: {str(e)}")
    
    # Add timestamp to the result
    result_with_timestamp = result.copy()
    result_with_timestamp['timestamp'] = datetime.now().isoformat()
    
    # Append the new failed endpoint
    failed_endpoints.append(result_with_timestamp)
    
    # Save the updated list
    try:
        with open(filepath, 'w') as f:
            json.dump(failed_endpoints, f, indent=2)
        logger.info(f"Saved failed endpoint to {filepath}")
    except Exception as e:
        logger.error(f"Error saving failed endpoint to {filepath}: {str(e)}")


def load_failed_endpoints() -> List[Dict[str, Any]]:
    """
    Load failed endpoints from the failed endpoints file.
    
    Returns:
        List of failed endpoint objects
    """
    filepath = os.path.join(OUTPUT_DIR, 'failed_endpoints.json')
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                failed_endpoints = json.load(f)
            logger.info(f"Loaded failed endpoints from {filepath}")
            return failed_endpoints
        else:
            logger.warning(f"File {filepath} not found, returning empty list")
            return []
    except Exception as e:
        logger.error(f"Error loading failed endpoints from {filepath}: {str(e)}")
        return []
