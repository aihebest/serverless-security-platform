# scripts/mock_vuln_db.py

from aiohttp import web
import json
from typing import Dict, List

# Mock vulnerability database
MOCK_VULNERABILITIES: Dict[str, List[Dict]] = {
    "requests": [
        {
            "severity": "HIGH",
            "description": "Mock vulnerability in requests package",
            "recommendation": "Update to latest version",
            "cve_id": "CVE-2024-MOCK-001"
        }
    ],
    "flask": [
        {
            "severity": "MEDIUM",
            "description": "Mock vulnerability in flask package",
            "recommendation": "Apply security patch",
            "cve_id": "CVE-2024-MOCK-002"
        }
    ]
}

async def health_check(request):
    return web.Response(text="OK", status=200)

async def get_vulnerabilities(request):
    try:
        package_info = json.loads(request.query.get('package', '{}'))
        package_name = package_info.get('name', '')
        
        vulnerabilities = MOCK_VULNERABILITIES.get(package_name, [])
        return web.json_response(vulnerabilities)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

def main():
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/vulnerabilities', get_vulnerabilities)
    
    print("Starting mock vulnerability database on http://localhost:8080")
    web.run_app(app, host='localhost', port=8080)

if __name__ == '__main__':
    main()