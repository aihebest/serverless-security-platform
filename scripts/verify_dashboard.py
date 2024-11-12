# scripts/verify_dashboard.py
import requests
import time
import sys

def test_dashboard_setup():
    endpoints = {
        'Function App': {
            'health': 'http://localhost:7071/api/health',
            'dashboard-data': 'http://localhost:7071/api/dashboard-data',
            'static-files': 'http://localhost:7071/api/static/css/styles.css'
        },
        'Dashboard': {
            'main': 'http://localhost:8080',
            'styles': 'http://localhost:8080/static/css/styles.css',
            'js': 'http://localhost:8080/static/js/dashboard.js'
        }
    }

    success = True

    for service, urls in endpoints.items():
        print(f"\nTesting {service}:")
        for name, url in urls.items():
            try:
                response = requests.get(url)
                status = '✓' if response.status_code == 200 else '✗'
                print(f"{status} {name}: {response.status_code}")
                if response.status_code != 200:
                    success = False
            except Exception as e:
                print(f"✗ {name}: Error - {str(e)}")
                success = False

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(test_dashboard_setup())