# demos/security_scan_demo.py
import sys
import os

# Add project root to Python path to allow imports from src
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import asyncio
import json
from src.scanners.scanning_service import ScanningService
from src.scanners.dependency_scanner import DependencyScanner
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import os

async def run_security_demo():
    """
    Demonstrates the security scanning capabilities of the platform
    """
    print("\n=== Starting Security Scanning Demo ===\n")
    
    # 1. Initialize Scanner
    print("1. Initializing Scanning Service...")
    scanning_service = ScanningService(
        scanner=DependencyScanner()
    )
    
    # 2. Prepare Test Dependencies
    print("\n2. Preparing Test Dependencies for Scan...")
    dependencies = [
        {"name": "requests", "version": "2.26.0"},
        {"name": "django", "version": "2.2.24"},
        {"name": "flask", "version": "2.0.1"}
    ]
    
    # 3. Run Dependency Scan
    print("\n3. Running Dependency Vulnerability Scan...")
    scan_results = await scanning_service.scan_dependencies(
        project_id="demo-project",
        dependencies=dependencies
    )
    
    # 4. Display Results
    print("\n4. Scan Results:")
    print("-" * 50)
    print(f"Total vulnerabilities found: {len(scan_results)}")
    
    for idx, vulnerability in enumerate(scan_results, 1):
        print(f"\nVulnerability {idx}:")
        print(f"Package: {vulnerability['package_name']} {vulnerability['package_version']}")
        print(f"Severity: {vulnerability['severity']}")
        print(f"Description: {vulnerability['description']}")
        print(f"Fix Version: {vulnerability.get('fixed_version', 'Not available')}")
    
    # 5. Retrieve from Storage
    print("\n5. Retrieving Results from Cosmos DB...")
    load_dotenv()
    cosmos_client = CosmosClient.from_connection_string(os.getenv("COSMOS_CONNECTION_STRING"))
    database = cosmos_client.get_database_client("security-db")
    container = database.get_container_client("scan-results")
    
    stored_results = container.query_items(
        query="SELECT * FROM c WHERE c.project_id = @project_id ORDER BY c._ts DESC",
        parameters=[{"name": "@project_id", "value": "demo-project"}],
        enable_cross_partition_query=True
    )
    
    print("\nStored Results Summary:")
    print("-" * 50)
    for result in stored_results:
        print(f"Scan ID: {result['id']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Total Findings: {len(result['vulnerabilities'])}")
        print(f"Highest Severity: {max(v['severity'] for v in result['vulnerabilities'])}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_security_demo())