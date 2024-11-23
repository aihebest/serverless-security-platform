# scripts/verify_dashboard.py
import os
import json
import asyncio
from datetime import datetime
from azure.cosmos import CosmosClient, exceptions
from azure.identity import DefaultAzureCredential

class DashboardMetricsProcessor:
    def __init__(self):
        try:
            connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING')
            if not connection_string:
                raise ValueError("COSMOS_DB_CONNECTION_STRING environment variable is not set")
                
            self.database_name = os.getenv('COSMOS_DB_DATABASE_NAME', 'SecurityFindings')
            self.container_name = os.getenv('COSMOS_DB_CONTAINER_NAME', 'SecurityScans')
            
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            
            # Ensure database exists
            print(f"Creating database if not exists: {self.database_name}")
            self.database = self.cosmos_client.create_database_if_not_exists(
                id=self.database_name,
                throughput=400
            )
            
            # Ensure container exists
            print(f"Creating container if not exists: {self.container_name}")
            self.container = self.database.create_container_if_not_exists(
                id=self.container_name,
                partition_key_path="/id"
            )
            
            print("✅ Database and container setup completed")
            
        except Exception as e:
            print(f"Failed to initialize Cosmos DB client: {str(e)}")
            raise

    async def update_dashboard_metrics(self):
        """Update dashboard with latest security metrics"""
        try:
            # Get scan results
            scan_results = self._load_scan_results()
            
            # Prepare metrics document
            metrics = {
                'id': f'metrics_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'timestamp': datetime.utcnow().isoformat(),
                'scan_results': scan_results,
                'security_score': self._calculate_security_score(scan_results)
            }
            
            # Store in Cosmos DB
            print("Storing metrics in Cosmos DB...")
            self.container.upsert_item(metrics)
            print("✅ Dashboard metrics updated successfully")
            
            # Save locally for debugging
            with open('dashboard_metrics.json', 'w') as f:
                json.dump(metrics, f, indent=2)
                
            print(f"Security Score: {metrics['security_score']}")
            return metrics
            
        except exceptions.CosmosResourceNotFoundError as e:
            print(f"Resource not found error: {str(e)}")
            print("Attempting to create required resources...")
            self.__init__()  # Reinitialize to create resources
            return await self.update_dashboard_metrics()
            
        except Exception as e:
            print(f"❌ Error updating dashboard metrics: {str(e)}")
            return {
                'id': f'metrics_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'status': 'failed',
                'error': str(e)
            }

    def _load_scan_results(self):
        """Load and process scan results files"""
        results = {}
        
        # Load SAST results if available
        try:
            with open('bandit-results.json', 'r') as f:
                results['sast'] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            results['sast'] = {'metrics': {'high': 0, 'medium': 0, 'low': 0}}
            
        # Load dependency check results if available
        try:
            with open('safety-results.json', 'r') as f:
                results['dependencies'] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            results['dependencies'] = []
            
        return results

    def _calculate_security_score(self, scan_results):
        """Calculate security score from scan results"""
        base_score = 100
        deductions = {
            'high': 10,
            'medium': 5,
            'low': 2
        }
        
        # Calculate score from SAST findings
        sast_metrics = scan_results.get('sast', {}).get('metrics', {})
        score = base_score
        for severity, count in sast_metrics.items():
            if severity in deductions:
                score -= count * deductions[severity]
                
        # Calculate score from dependency findings
        deps = scan_results.get('dependencies', [])
        for dep in deps:
            severity = dep.get('severity', 'low').lower()
            if severity in deductions:
                score -= deductions[severity]
                
        return max(0, score)

async def main():
    try:
        processor = DashboardMetricsProcessor()
        metrics = await processor.update_dashboard_metrics()
        print("Security Scan Results:")
        print(json.dumps(metrics, indent=2))
        
    except Exception as e:
        print(f"Failed to update dashboard: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())