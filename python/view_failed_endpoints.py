#!/usr/bin/env python3
"""
Script to view failed endpoints from the failed_endpoints.json file.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List

from config import OUTPUT_DIR

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='View failed endpoints from regression tests')
    
    parser.add_argument(
        '--since',
        type=str,
        help='Show only failures since this time (format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)'
    )
    
    parser.add_argument(
        '--endpoint',
        type=str,
        help='Filter by endpoint (e.g., collections, collections/bukhari)'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show only summary information, not individual failures'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear the failed endpoints file after viewing'
    )
    
    return parser.parse_args()


def load_failed_endpoints():
    """Load failed endpoints from the JSON file."""
    filepath = os.path.join(OUTPUT_DIR, 'failed_endpoints.json')
    
    if not os.path.exists(filepath):
        print(f"No failed endpoints file found at {filepath}")
        return []
    
    try:
        with open(filepath, 'r') as f:
            failed_endpoints = json.load(f)
        return failed_endpoints
    except Exception as e:
        print(f"Error loading failed endpoints: {str(e)}")
        return []


def clear_failed_endpoints():
    """Clear the failed endpoints file."""
    filepath = os.path.join(OUTPUT_DIR, 'failed_endpoints.json')
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump([], f)
            print(f"Cleared failed endpoints file at {filepath}")
        except Exception as e:
            print(f"Error clearing failed endpoints: {str(e)}")


def parse_datetime(dt_str):
    """Parse a datetime string into a datetime object."""
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse datetime string: {dt_str}")


def main():
    """Main function to view failed endpoints."""
    args = parse_args()
    
    # Load failed endpoints
    failed_endpoints = load_failed_endpoints()
    
    if not failed_endpoints:
        print("No failed endpoints found.")
        return 0
    
    # Filter by time if specified
    if args.since:
        try:
            since_dt = parse_datetime(args.since)
            failed_endpoints = [
                f for f in failed_endpoints 
                if 'timestamp' in f and parse_datetime(f['timestamp']) >= since_dt
            ]
            print(f"Showing failures since {args.since}")
        except ValueError as e:
            print(f"Error parsing since date: {str(e)}")
            return 1
    
    # Filter by endpoint if specified
    if args.endpoint:
        failed_endpoints = [
            f for f in failed_endpoints 
            if f.get('endpoint', '').startswith(args.endpoint)
        ]
        print(f"Showing failures for endpoint: {args.endpoint}")
    
    if not failed_endpoints:
        print("No failed endpoints match the specified filters.")
        return 0
    
    # Group by endpoint
    endpoint_failures = {}
    for failure in failed_endpoints:
        endpoint = failure.get('endpoint', 'unknown')
        if endpoint not in endpoint_failures:
            endpoint_failures[endpoint] = []
        endpoint_failures[endpoint].append(failure)
    
    # Print summary
    print("=" * 80)
    print(f"Failed Endpoints Summary ({len(failed_endpoints)} total failures)")
    print("=" * 80)
    
    for endpoint, failures in endpoint_failures.items():
        print(f"{endpoint}: {len(failures)} failures")
    
    # Print details if not summary only
    if not args.summary:
        print("\n" + "=" * 80)
        print("Failure Details")
        print("=" * 80)
        
        for endpoint, failures in endpoint_failures.items():
            print(f"\n{endpoint}:")
            
            for i, failure in enumerate(failures, 1):
                timestamp = failure.get('timestamp', 'unknown')
                params = failure.get('params', 'None')
                differences = failure.get('differences', [])
                
                print(f"  Failure {i} at {timestamp}")
                if params != 'None':
                    print(f"  Parameters: {params}")
                
                if differences:
                    print("  Differences:")
                    for diff in differences[:5]:  # Show only first 5 differences
                        print(f"    - {diff}")
                    
                    if len(differences) > 5:
                        print(f"    ... and {len(differences) - 5} more differences")
                
                print()
    
    # Clear the file if requested
    if args.clear:
        clear_failed_endpoints()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
