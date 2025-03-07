"""
Utility for comparing API responses from two different implementations.
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional

from deepdiff import DeepDiff

from api_client import ApiResponse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('response_comparator')


class ComparisonResult:
    """Class to represent the result of comparing two API responses."""
    
    def __init__(self, 
                 is_equal: bool, 
                 differences: List[str] = None, 
                 endpoint: str = None, 
                 params: Dict[str, Any] = None):
        self.is_equal = is_equal
        self.differences = differences or []
        self.endpoint = endpoint
        self.params = params
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the comparison result to a dictionary."""
        return {
            'is_equal': self.is_equal,
            'differences': self.differences,
            'endpoint': self.endpoint,
            'params': self.params
        }
    
    def __str__(self) -> str:
        """String representation of the comparison result."""
        if self.is_equal:
            return f"✅ Responses match for {self.endpoint}"
        else:
            return f"❌ Responses differ for {self.endpoint}: {len(self.differences)} differences"


def compare_responses(response1: ApiResponse, response2: ApiResponse, 
                     endpoint: str = None, params: Dict[str, Any] = None) -> ComparisonResult:
    """
    Compare two API responses and return a comparison result.
    
    Args:
        response1: First API response
        response2: Second API response
        endpoint: The API endpoint (for reporting)
        params: Query parameters (for reporting)
        
    Returns:
        ComparisonResult object
    """
    differences = []
    
    # Compare status codes
    if response1.status_code != response2.status_code:
        differences.append(f"Status codes differ: {response1.status_code} vs {response2.status_code}")
    
    # If either response has an error, add it to the differences
    if response1.error:
        differences.append(f"API1 error: {response1.error}")
    if response2.error:
        differences.append(f"API2 error: {response2.error}")
    
    # Compare response bodies if both are successful
    if response1.is_success() and response2.is_success():
        try:
            # Use DeepDiff for semantic comparison
            diff = DeepDiff(response1.body, response2.body, ignore_order=True)
            
            if diff:
                # Add each difference to the list
                for diff_type, diff_items in diff.items():
                    if isinstance(diff_items, dict):
                        for path, value in diff_items.items():
                            differences.append(f"{diff_type}: {path} - {value}")
                    else:
                        differences.append(f"{diff_type}: {diff_items}")
        except Exception as e:
            differences.append(f"Error comparing response bodies: {str(e)}")
    
    # Create and return the comparison result
    is_equal = len(differences) == 0
    result = ComparisonResult(is_equal, differences, endpoint, params)
    
    # Log the result
    if is_equal:
        logger.info(f"✅ Responses match for {endpoint}")
    else:
        logger.error(f"❌ Responses differ for {endpoint}")
        for diff in differences:
            logger.error(f"  - {diff}")
    
    return result


def compare_paginated_responses(response1: ApiResponse, response2: ApiResponse,
                               endpoint: str = None, params: Dict[str, Any] = None) -> ComparisonResult:
    """
    Compare two paginated API responses, focusing on the data content.
    
    Args:
        response1: First API response
        response2: Second API response
        endpoint: The API endpoint (for reporting)
        params: Query parameters (for reporting)
        
    Returns:
        ComparisonResult object
    """
    differences = []
    
    # Compare status codes
    if response1.status_code != response2.status_code:
        differences.append(f"Status codes differ: {response1.status_code} vs {response2.status_code}")
    
    # If either response has an error, add it to the differences
    if response1.error:
        differences.append(f"API1 error: {response1.error}")
    if response2.error:
        differences.append(f"API2 error: {response2.error}")
    
    # Compare response bodies if both are successful
    if response1.is_success() and response2.is_success():
        try:
            # Extract pagination metadata
            pagination1 = {k: v for k, v in response1.body.items() if k != 'data'} if isinstance(response1.body, dict) else {}
            pagination2 = {k: v for k, v in response2.body.items() if k != 'data'} if isinstance(response2.body, dict) else {}
            
            # Compare pagination metadata
            pagination_diff = DeepDiff(pagination1, pagination2, ignore_order=True)
            if pagination_diff:
                for diff_type, diff_items in pagination_diff.items():
                    if isinstance(diff_items, dict):
                        for path, value in diff_items.items():
                            differences.append(f"Pagination {diff_type}: {path} - {value}")
                    else:
                        differences.append(f"Pagination {diff_type}: {diff_items}")
            
            # Extract and compare data items
            data1 = response1.body.get('data', []) if isinstance(response1.body, dict) else []
            data2 = response2.body.get('data', []) if isinstance(response2.body, dict) else []
            
            # Compare data length
            if len(data1) != len(data2):
                differences.append(f"Data length differs: {len(data1)} vs {len(data2)}")
            
            # Compare data items
            data_diff = DeepDiff(data1, data2, ignore_order=True)
            if data_diff:
                for diff_type, diff_items in data_diff.items():
                    if isinstance(diff_items, dict):
                        for path, value in diff_items.items():
                            differences.append(f"Data {diff_type}: {path} - {value}")
                    else:
                        differences.append(f"Data {diff_type}: {diff_items}")
        
        except Exception as e:
            differences.append(f"Error comparing response bodies: {str(e)}")
    
    # Create and return the comparison result
    is_equal = len(differences) == 0
    result = ComparisonResult(is_equal, differences, endpoint, params)
    
    # Log the result
    if is_equal:
        logger.info(f"✅ Paginated responses match for {endpoint}")
    else:
        logger.error(f"❌ Paginated responses differ for {endpoint}")
        for diff in differences:
            logger.error(f"  - {diff}")
    
    return result


def format_comparison_for_report(result: ComparisonResult) -> Dict[str, Any]:
    """
    Format a comparison result for inclusion in a test report.
    
    Args:
        result: The comparison result
        
    Returns:
        Dictionary with formatted comparison data
    """
    status = "PASS" if result.is_equal else "FAIL"
    params_str = json.dumps(result.params) if result.params else "None"
    
    return {
        'endpoint': result.endpoint,
        'params': params_str,
        'status': status,
        'differences': result.differences
    }
