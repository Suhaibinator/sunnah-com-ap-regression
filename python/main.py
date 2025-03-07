"""
Main script to run all API regression tests.
"""

import os
import sys
import logging
import argparse
import time
from typing import Dict, Any, List

from test_collections import run_collections_tests
from test_books import run_books_tests
from test_hadiths import run_hadiths_tests
from report_generator import generate_html_report, generate_json_report
from data_store import load_failed_endpoints
from config import OUTPUT_DIR, API_IMPL1, API_IMPL2

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(OUTPUT_DIR, 'test_run.log'))
    ]
)
logger = logging.getLogger('main')


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run API regression tests')
    
    parser.add_argument(
        '--collections-only',
        action='store_true',
        help='Run only collections tests'
    )
    
    parser.add_argument(
        '--books-only',
        action='store_true',
        help='Run only books tests'
    )
    
    parser.add_argument(
        '--hadiths-only',
        action='store_true',
        help='Run only hadiths tests'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Do not generate HTML and JSON reports'
    )
    
    return parser.parse_args()


def main():
    """Run all tests and generate reports."""
    args = parse_args()
    
    start_time = time.time()
    logger.info("Starting API regression tests")
    
    # Log API configuration
    logger.info("API Configuration:")
    logger.info(f"API1 Base URL: {API_IMPL1['base_url']}")
    # Mask the API key for security (show first 4 chars)
    api1_key_masked = API_IMPL1['api_key'][:4] + '*' * (len(API_IMPL1['api_key']) - 4) if API_IMPL1['api_key'] else 'Not set'
    logger.info(f"API1 Key: {api1_key_masked}")
    
    logger.info(f"API2 Base URL: {API_IMPL2['base_url']}")
    api2_key_masked = API_IMPL2['api_key'][:4] + '*' * (len(API_IMPL2['api_key']) - 4) if API_IMPL2['api_key'] else 'Not set'
    logger.info(f"API2 Key: {api2_key_masked}")
    
    all_results = []
    
    # Run collections tests
    if not args.books_only and not args.hadiths_only:
        logger.info("Running collections tests")
        collections_results = run_collections_tests()
        all_results.extend(collections_results)
        logger.info(f"Completed collections tests: {len(collections_results)} tests run")
    
    # Run books tests
    if not args.collections_only and not args.hadiths_only:
        logger.info("Running books tests")
        books_results = run_books_tests()
        all_results.extend(books_results)
        logger.info(f"Completed books tests: {len(books_results)} tests run")
    
    # Run hadiths tests
    if not args.collections_only and not args.books_only:
        logger.info("Running hadiths tests")
        hadiths_results = run_hadiths_tests()
        all_results.extend(hadiths_results)
        logger.info(f"Completed hadiths tests: {len(hadiths_results)} tests run")
    
    # Generate reports
    if not args.no_report:
        logger.info("Generating reports")
        html_report_path = generate_html_report(all_results)
        json_report_path = generate_json_report(all_results)
        logger.info(f"Reports generated at {html_report_path} and {json_report_path}")
    
    # Calculate statistics
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r['status'] == 'PASS')
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Log summary
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info("=" * 80)
    logger.info("API Regression Test Summary")
    logger.info("=" * 80)
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {failed_tests}")
    logger.info(f"Pass Rate: {pass_rate:.2f}%")
    logger.info(f"Duration: {duration:.2f} seconds")
    
    # Load and display failed endpoints
    failed_endpoints = load_failed_endpoints()
    if failed_endpoints:
        logger.info("=" * 80)
        logger.info("Failed Endpoints")
        logger.info("=" * 80)
        logger.info(f"Total Failed Endpoints: {len(failed_endpoints)}")
        logger.info("Failed endpoints are saved to: output/failed_endpoints.json")
        
        # Group by endpoint
        endpoint_failures = {}
        for failure in failed_endpoints:
            endpoint = failure.get('endpoint', 'unknown')
            if endpoint not in endpoint_failures:
                endpoint_failures[endpoint] = 0
            endpoint_failures[endpoint] += 1
        
        # Display summary of failed endpoints
        for endpoint, count in endpoint_failures.items():
            logger.info(f"  - {endpoint}: {count} failures")
    
    logger.info("=" * 80)
    
    # Return exit code based on test results
    return 0 if failed_tests == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
