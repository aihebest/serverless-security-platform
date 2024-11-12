# src/scanners/scanning_service.py
import os
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from azure.cosmos import CosmosClient
from .compliance_scanner import ComplianceScanner

logger = logging.getLogger(__name__)

class ScanningService:
    def __init__(self):
        self.compliance_scanner = ComplianceScanner()
        
        # Initialize Cosmos DB client if connection string is available
        cosmos_connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING')
        if cosmos_connection_string:
            self.cosmos_client = CosmosClient.from_connection_string(cosmos_connection_string)
            self.database = self.cosmos_client.get_database_client(
                os.getenv('COSMOS_DB_DATABASE_NAME')
            )
            self.container = self.database.get_container_client(
                os.getenv('COSMOS_DB_CONTAINER_NAME')
            )
        else:
            logger.warning("No Cosmos DB connection string provided")
            self.cosmos_client = None

    async def run_scan(self) -> Dict[str, Any]:
        """Run complete security scan"""
        try:
            scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Starting security scan {scan_id}")

            # Run compliance scan
            compliance_results = await self.compliance_scanner.scan()

            # Combine results
            results = {
                'scan_id': scan_id,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'completed',
                'compliance_scan': compliance_results
            }

            # Store results if Cosmos DB is available
            if self.cosmos_client:
                await self._store_results(results)

            logger.info(f"Security scan {scan_id} completed successfully")
            return results

        except Exception as e:
            error_msg = f"Security scan failed: {str(e)}"
            logger.error(error_msg)
            return {
                'scan_id': scan_id if 'scan_id' in locals() else 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'failed',
                'error': error_msg
            }

    async def _store_results(self, results: Dict[str, Any]):
        """Store scan results in Cosmos DB"""
        try:
            if self.cosmos_client:
                self.container.create_item(body=results)
                logger.info(f"Stored scan results for {results['scan_id']}")
        except Exception as e:
            logger.error(f"Failed to store scan results: {str(e)}")