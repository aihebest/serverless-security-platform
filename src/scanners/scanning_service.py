# src/scanners/scanning_service.py

import os
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from .dependency_scanner import DependencyScanner
from .compliance_scanner import ComplianceScanner

logger = logging.getLogger(__name__)

class ScanningService:
    def __init__(self):
        self.connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING')
        self.database_name = os.getenv('COSMOS_DB_DATABASE_NAME')
        self.container_name = os.getenv('COSMOS_DB_CONTAINER_NAME')
        
        # Initialize scanners
        self.dependency_scanner = DependencyScanner()
        self.compliance_scanner = ComplianceScanner()
        
        # Initialize Cosmos DB client
        self._initialize_cosmos_client()

    def _initialize_cosmos_client(self):
        """Initialize Cosmos DB client with error handling"""
        try:
            if not self.connection_string:
                raise ValueError("COSMOS_DB_CONNECTION_STRING environment variable is not set")
            
            self.cosmos_client = CosmosClient.from_connection_string(self.connection_string)
            self.database = self.cosmos_client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            
            logger.info("Successfully initialized Cosmos DB client")
            
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB client: {str(e)}")
            # Continue without Cosmos DB for basic scanning
            self.cosmos_client = None
            self.database = None
            self.container = None

    async def run_scan(self) -> Dict[str, Any]:
        """Run all security scans"""
        try:
            scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Starting security scan {scan_id}")
            
            # Run dependency scan
            dependencies = [
                {"name": "requests", "version": "2.26.0"},
                {"name": "azure-cosmos", "version": "4.3.0"}
            ]
            
            dependency_results = await self.dependency_scanner.scan(dependencies)
            
            # Run compliance scan
            config = self._get_compliance_config()
            compliance_results = await self.compliance_scanner.scan(config)
            
            # Combine results
            results = {
                'scan_id': scan_id,
                'timestamp': datetime.utcnow().isoformat(),
                'dependency_scan': dependency_results,
                'compliance_scan': compliance_results
            }
            
            # Store results if Cosmos DB is available
            if self.container:
                await self._store_results(results)
            
            return results
            
        except Exception as e:
            error_msg = f"Security scan failed: {str(e)}"
            logger.error(error_msg)
            return {
                'scan_id': scan_id,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'failed',
                'error': error_msg
            }

    def _get_compliance_config(self) -> Dict[str, Any]:
        """Get compliance configuration"""
        return {
            'password_policy': {
                'min_length': 12,
                'require_special_chars': True,
                'require_numbers': True
            },
            'encryption': {
                'require_tls': True,
                'require_at_rest': True
            },
            'access_control': {
                'require_mfa': True,
                'require_rbac': True
            }
        }

    async def _store_results(self, results: Dict[str, Any]):
        """Store scan results in Cosmos DB"""
        try:
            if self.container:
                await self.container.create_item(body=results)
                logger.info(f"Stored scan results with ID: {results['scan_id']}")
        except Exception as e:
            logger.error(f"Failed to store scan results: {str(e)}")
            # Continue without storing results

if __name__ == "__main__":
    async def main():
        scanner = ScanningService()
        results = await scanner.run_scan()
        print(json.dumps(results, indent=2))

    asyncio.run(main())