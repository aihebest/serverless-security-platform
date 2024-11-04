# scripts/test_scanner.py

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scanners.base_scanner import BaseScanner, ScanResult
from src.scanners.dependency_scanner import DependencyScanner

async def test_scanner(scanner: BaseScanner) -> Dict:
    print(f"\nTesting {scanner.__class__.__name__}...")
    
    try:
        # Test configuration validation
        print("Validating configuration...")
        config_valid = await scanner.validate_configuration()
        if not config_valid:
            return {"status": "failed", "error": "Configuration validation failed"}
        
        # Execute scan
        print("Executing scan...")
        results = await scanner.execute_scan()
        
        # Analyze results
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for result in results:
            severity_counts[result.severity] += 1
        
        return {
            "status": "success",
            "total_findings": len(results),
            "severity_counts": severity_counts,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

async def main():
    # Test configuration
    config = {
        "vulnerability_database_url": "http://localhost:8080",
        "scan_depth": "DEEP",
        "alert_thresholds": {
            "HIGH": 1,
            "MEDIUM": 5,
            "LOW": 10
        }
    }
    
    # Initialize scanner
    scanner = DependencyScanner(config)
    
    # Run test
    result = await test_scanner(scanner)
    
    # Print results
    print("\nTest Results:")
    print("-" * 40)
    for key, value in result.items():
        print(f"{key}: {value}")
    
    return 0 if result["status"] == "success" else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))