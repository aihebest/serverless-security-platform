# scripts/test_functions.py

import requests
import json
from typing import Dict, Any

def test_azure_function(endpoint: str) -> Dict[str, Any]:
    # Remove 'api/' from the URL as we've removed the route prefix
    url = f"http://localhost:7071/{endpoint}"
    print(f"\nTesting endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'json' in content_type:
                try:
                    data = response.json()
                    print("Response data sample:", json.dumps(data, indent=2)[:200] + "...")
                except:
                    print("Response text:", response.text[:200])
            else:
                print(f"Content-Type: {content_type}")
                print("Response length:", len(response.content))
        
        return {
            "endpoint": endpoint,
            "status": response.status_code,
            "success": response.status_code == 200,
            "content_type": response.headers.get('content-type', '')
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "endpoint": endpoint,
            "status": 0,
            "success": False,
            "error": str(e)
        }

def main():
    # Test each endpoint
    endpoints = [
        "health",  # Changed from api/health
        "dashboard-data",  # Changed from api/dashboard-data
        "static/css/styles.css",
        "static/js/dashboard.js"
    ]
    
    print("Testing Azure Functions endpoints...")
    results = []
    
    for endpoint in endpoints:
        result = test_azure_function(endpoint)
        results.append(result)
        
        # Print detailed status
        status = "✓" if result["success"] else "✗"
        print(f"\n{status} {endpoint}:")
        print(f"  Status: {result['status']}")
        print(f"  Content-Type: {result.get('content_type', 'N/A')}")
        if "error" in result:
            print(f"  Error: {result['error']}")
    
    # Summary
    print("\nTest Summary:")
    print("-" * 40)
    successful = sum(1 for r in results if r["success"])
    print(f"Successful: {successful}/{len(endpoints)}")
    
    return 0 if successful == len(endpoints) else 1

if __name__ == "__main__":
    exit(main())