# scripts/verify_setup.py
import requests
import json
import sys

def verify_setup():
    base_url = "http://localhost:7071"
    
    # Test endpoints
    endpoints = [
        "/api/health",
        "/api/dashboard-data",
        "/api/dashboard",
        "/api/static/js/dashboard.js"
    ]
    
    failed = False
    
    print("Verifying setup...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} {endpoint}: {response.status_code}")
            if response.status_code != 200:
                failed = True
        except Exception as e:
            print(f"✗ {endpoint}: Error - {str(e)}")
            failed = True
    
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(verify_setup())