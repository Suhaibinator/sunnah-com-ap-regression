"""
Generate HTML reports from test results.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from config import OUTPUT_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('report_generator')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_html_report(results: List[Dict[str, Any]], title: str = "API Regression Test Report") -> str:
    """
    Generate an HTML report from test results.
    
    Args:
        results: List of test results
        title: Report title
        
    Returns:
        Path to the generated HTML report
    """
    # Count pass/fail results
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['status'] == 'PASS')
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Group results by endpoint
    endpoint_results = {}
    for result in results:
        endpoint = result['endpoint']
        if endpoint not in endpoint_results:
            endpoint_results[endpoint] = []
        endpoint_results[endpoint].append(result)
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #444;
            }}
            .summary {{
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .summary-item {{
                margin-bottom: 10px;
            }}
            .pass-rate {{
                font-size: 24px;
                font-weight: bold;
                color: {('#4CAF50' if pass_rate >= 90 else '#FF9800' if pass_rate >= 70 else '#F44336')};
            }}
            .endpoint-group {{
                margin-bottom: 30px;
                border: 1px solid #ddd;
                border-radius: 5px;
                overflow: hidden;
            }}
            .endpoint-header {{
                background-color: #f0f0f0;
                padding: 10px 15px;
                cursor: pointer;
                border-bottom: 1px solid #ddd;
            }}
            .endpoint-content {{
                padding: 0;
            }}
            .test-result {{
                padding: 10px 15px;
                border-bottom: 1px solid #eee;
            }}
            .test-result:last-child {{
                border-bottom: none;
            }}
            .pass {{
                border-left: 5px solid #4CAF50;
            }}
            .fail {{
                border-left: 5px solid #F44336;
            }}
            .params {{
                font-family: monospace;
                background-color: #f9f9f9;
                padding: 5px;
                border-radius: 3px;
                margin-top: 5px;
            }}
            .differences {{
                margin-top: 10px;
                padding-left: 20px;
            }}
            .difference-item {{
                font-family: monospace;
                color: #F44336;
                margin-bottom: 5px;
            }}
            .toggle-btn {{
                background: none;
                border: none;
                cursor: pointer;
                float: right;
                font-size: 16px;
            }}
            .hidden {{
                display: none;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="summary">
            <div class="summary-item">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div class="summary-item">Total Tests: {total_tests}</div>
            <div class="summary-item">Passed: {passed_tests}</div>
            <div class="summary-item">Failed: {failed_tests}</div>
            <div class="summary-item">Pass Rate: <span class="pass-rate">{pass_rate:.2f}%</span></div>
        </div>
        
        <h2>Results by Endpoint</h2>
    """
    
    # Add results for each endpoint
    for endpoint, endpoint_results_list in endpoint_results.items():
        endpoint_pass = sum(1 for r in endpoint_results_list if r['status'] == 'PASS')
        endpoint_total = len(endpoint_results_list)
        endpoint_pass_rate = (endpoint_pass / endpoint_total) * 100 if endpoint_total > 0 else 0
        
        html += f"""
        <div class="endpoint-group">
            <div class="endpoint-header" onclick="toggleEndpoint(this)">
                {endpoint} ({endpoint_pass}/{endpoint_total} passed, {endpoint_pass_rate:.2f}%)
                <button class="toggle-btn">▼</button>
            </div>
            <div class="endpoint-content">
        """
        
        for result in endpoint_results_list:
            status_class = "pass" if result['status'] == 'PASS' else "fail"
            params = result['params']
            
            html += f"""
            <div class="test-result {status_class}">
                <div><strong>Status:</strong> {result['status']}</div>
            """
            
            if params and params != 'None':
                html += f"""
                <div><strong>Parameters:</strong></div>
                <div class="params">{params}</div>
                """
            
            if result['status'] == 'FAIL' and result['differences']:
                html += f"""
                <div><strong>Differences:</strong></div>
                <div class="differences">
                """
                
                for diff in result['differences']:
                    html += f"""
                    <div class="difference-item">{diff}</div>
                    """
                
                html += "</div>"
            
            html += "</div>"
        
        html += """
            </div>
        </div>
        """
    
    html += """
        <script>
            function toggleEndpoint(header) {
                const content = header.nextElementSibling;
                content.classList.toggle('hidden');
                const btn = header.querySelector('.toggle-btn');
                btn.textContent = content.classList.contains('hidden') ? '▶' : '▼';
            }
            
            // Initialize all endpoint contents as visible
            document.addEventListener('DOMContentLoaded', function() {
                const headers = document.querySelectorAll('.endpoint-header');
                headers.forEach(header => {
                    const btn = header.querySelector('.toggle-btn');
                    btn.textContent = '▼';
                });
            });
        </script>
    </body>
    </html>
    """
    
    # Write HTML to file
    report_path = os.path.join(OUTPUT_DIR, 'report.html')
    with open(report_path, 'w') as f:
        f.write(html)
    
    logger.info(f"Generated HTML report at {report_path}")
    return report_path


def generate_json_report(results: List[Dict[str, Any]]) -> str:
    """
    Generate a JSON report from test results.
    
    Args:
        results: List of test results
        
    Returns:
        Path to the generated JSON report
    """
    # Count pass/fail results
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['status'] == 'PASS')
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Create report data
    report_data = {
        'summary': {
            'generated': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'pass_rate': pass_rate
        },
        'results': results
    }
    
    # Write JSON to file
    report_path = os.path.join(OUTPUT_DIR, 'report.json')
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    logger.info(f"Generated JSON report at {report_path}")
    return report_path
