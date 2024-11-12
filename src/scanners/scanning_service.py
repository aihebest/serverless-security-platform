# src/scanners/scanning_service.py

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from azure.cosmos import CosmosClient
from .dependency_scanner import DependencyScanner
from .compliance_scanner import ComplianceScanner

logger = logging.getLogger(__name__)

class ScanningService:
    def __init__(self):
        # Initialize cosmos client
        self.cosmos_client = CosmosClient.from_connection_string(os.getenv('COSMOS_DB_CONNECTION_STRING'))
        self.database = self.cosmos_client.get_database_client(os.getenv('COSMOS_DB_DATABASE_NAME'))
        self.container = self.database.get_container_client(os.getenv('COSMOS_DB_CONTAINER_NAME'))
        
        # Initialize scanners
        self.dependency_scanner = DependencyScanner()
        self.compliance_scanner = ComplianceScanner(logger=logger)

    async def scan_all(self) -> Dict[str, Any]:
        """Run all security scans"""
        try:
            # Run scans in parallel
            dependency_task = self.scan_dependencies([])  # Add your dependencies list here
            compliance_task = self.scan_compliance()
            
            # Wait for all scans to complete
            scan_results = await asyncio.gather(
                dependency_task,
                compliance_task,
                return_exceptions=True
            )
            
            # Combine results
            combined_results = {
                'scan_id': f"full-scan-{datetime.utcnow().isoformat()}",
                'timestamp': datetime.utcnow().isoformat(),
                'dependency_scan': scan_results[0] if not isinstance(scan_results[0], Exception) else str(scan_results[0]),
                'compliance_scan': scan_results[1] if not isinstance(scan_results[1], Exception) else str(scan_results[1])
            }
            
            # Store combined results
            await self._store_scan_results(combined_results)
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Full scan failed: {str(e)}")
            raise

    async def scan_dependencies(self, dependencies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Run dependency security scan"""
        try:
            logger.info(f"Starting dependency scan for {len(dependencies)} packages")
            results = await self.dependency_scanner.scan(dependencies)
            await self._store_scan_results(results)
            return results
        except Exception as e:
            logger.error(f"Dependency scan failed: {str(e)}")
            raise

    async def scan_compliance(self) -> Dict[str, Any]:
        """Run compliance scan"""
        try:
            logger.info("Starting compliance scan")
            # Load your configuration
            config = {
                'password_policy': {
                    'min_length': 12,
                    'require_special_chars': True,
                    'require_numbers': True,
                    'max_age_days': 90
                },
                'encryption': {
                    'require_tls': True,
                    'min_tls_version': '1.2',
                    'require_at_rest': True
                },
                'access_control': {
                    'require_mfa': True,
                    'max_session_duration': 12,
                    'require_rbac': True
                }
            }
            
            results = await self.compliance_scanner.scan(config)
            await self._store_scan_results(results)
            return results
        except Exception as e:
            logger.error(f"Compliance scan failed: {str(e)}")
            raise

    async def _store_scan_results(self, results: Dict[str, Any]):
        """Store scan results in Cosmos DB"""
        try:
            # Add metadata
            results['timestamp'] = datetime.utcnow().isoformat()
            results['type'] = 'scan_result'
            
            # Store in Cosmos DB
            await self.container.create_item(body=results)
            logger.info(f"Stored scan results with ID: {results.get('scan_id')}")
            
        except Exception as e:
            logger.error(f"Failed to store scan results: {str(e)}")
            raise

    async def get_scan_results(self, scan_id: str) -> Dict[str, Any]:
        """Retrieve scan results by ID"""
        try:
            query = f"SELECT * FROM c WHERE c.scan_id = '{scan_id}'"
            results = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Failed to retrieve scan results: {str(e)}")
            raise

    async def get_recent_scans(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent scan results"""
        try:
            query = "SELECT * FROM c WHERE c.type = 'scan_result' ORDER BY c.timestamp DESC OFFSET 0 LIMIT @limit"
            parameters = [{"name": "@limit", "value": limit}]
            results = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve recent scans: {str(e)}")
            raise