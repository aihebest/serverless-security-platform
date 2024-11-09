# scripts/test_e2e.py

import requests
import time
import json
import sys
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class E2ETester:
    def __init__(self):
        self.api_base = "http://localhost:7071"
        self.dashboard_url = "http://localhost:8080"
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results with details"""
        result = {"name": name, "success": success, "details": details}
        self.test_results.append(result)
        status = "✓" if success else "✗"
        logger.info(f"{status} {name}: {details}")

    async def test_api_endpoints(self) -> bool:
        """Test all API endpoints"""
        endpoints = {
            "Health Check": "/health",
            "Dashboard Data": "/dashboard-data",
            "CSS Files": "/static/css/styles.css",
            "JavaScript Files": "/static/js/dashboard.js"
        }

        all_passed = True
        for name, endpoint in endpoints.items():
            try:
                response = requests.get(f"{self.api_base}{endpoint}")
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                
                if success and endpoint == "/dashboard-data":
                    data = response.json()
                    details += f"\nSecurity Score: {data['security_score']['current']}"

                self.log_test(name, success, details)
                all_passed &= success
            except Exception as e:
                self.log_test(name, False, f"Error: {str(e)}")
                all_passed = False

        return all_passed

    async def test_dashboard_functionality(self) -> bool:
        """Test dashboard features"""
        try:
            response = requests.get(self.dashboard_url)
            success = response.status_code == 200
            self.log_test("Dashboard Access", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Dashboard Access", False, f"Error: {str(e)}")
            return False

    async def test_security_scanning(self) -> bool:
        """Test security scanning functionality"""
        try:
            response = requests.get(f"{self.api_base}/scan/dependencies")
            success = response.status_code == 200
            details = "Scan completed successfully" if success else "Scan failed"
            self.log_test("Security Scanning", success, details)
            return success
        except Exception as e:
            self.log_test("Security Scanning", False, f"Error: {str(e)}")
            return False

    def generate_report(self):
        """Generate test report"""
        print("\nE2E Test Report")
        print("=" * 50)
        
        categories = {
            "API": ["Health Check", "Dashboard Data"],
            "Static Files": ["CSS Files", "JavaScript Files"],
            "Features": ["Dashboard Access", "Security Scanning"]
        }

        for category, tests in categories.items():
            print(f"\n{category}:")
            for test in tests:
                result = next((r for r in self.test_results if r["name"] == test), None)
                if result:
                    status = "✓" if result["success"] else "✗"
                    print(f"{status} {test}")
                    if result["details"]:
                        print(f"  Details: {result['details']}")

        success_rate = sum(1 for r in self.test_results if r["success"]) / len(self.test_results) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")

async def main():
    tester = E2ETester()
    
    try:
        logger.info("Starting E2E tests...")
        
        # Run tests
        api_success = await tester.test_api_endpoints()
        dashboard_success = await tester.test_dashboard_functionality()
        scanning_success = await tester.test_security_scanning()
        
        # Generate report
        tester.generate_report()
        
        # Return overall success
        return all([api_success, dashboard_success, scanning_success])
    
    except Exception as e:
        logger.error(f"E2E test failed: {str(e)}")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)