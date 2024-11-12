# scripts/test_setup.py

import requests
import time
from typing import Dict, Any

def test_endpoint(url: str) -> Dict[str, Any]:
    try:
        response = requests.get(url)
        return {
            "status": response.status_code,
            "success": response.status_code == 200,
            "content_type": response.headers.get('content-type'),
        }
    except Exception as e:
        return {
            "status": 0,
            "success": False,
            "error": str(e)
        }

def main():
    # Test endpoints
    endpoints = {
        "Azure Functions": {
            "Health": "http://localhost:7071/api/health",
            "Dashboard Data": "http://localhost:7071/api/dashboard-data",
            "Static CSS": "http://localhost:7071/api/static/css/styles.css",
            "Static JS": "http://localhost:7071/api/static/js/dashboard.js"
        },
        "Dashboard Server": {
            "Main Page": "http://localhost:8080",
            "Static CSS": "http://localhost:8080/static/css/styles.css",
            "Static JS": "http://localhost:8080/static/js/dashboard.js"
        }
    }

    print("Testing setup...")
    all_passed = True

    for service, routes in endpoints.items():
        print(f"\n{service}:")
        for name, url in routes.items():
            result = test_endpoint(url)
            status = "✓" if result["success"] else "✗"
            print(f"{status} {name}: {result['status']}")
            if not result["success"]:
                all_passed = False
                if "error" in result:
                    print(f"  Error: {result['error']}")

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())