# scripts/verify_dashboard.py
import os
import json
import asyncio
from datetime import datetime
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

class DashboardMetricsProcessor:
    def __init__(self):
        try:
            connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING')
            if not connection_string:
                raise ValueError("COSMOS_DB_CONNECTION_STRING environment variable is not set")
                
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            self.database = self.cosmos_client.get_database_client(
                os.getenv('COSMOS_DB_DATABASE_NAME', 'security-platform')
            )
            self.container = self.database.get_container_client(
                os.getenv('COSMOS_DB_CONTAINER_NAME', 'security-metrics')
            )
        except Exception as e:
            print(f"Failed to initialize Cosmos DB client: {str(e)}")
            raise

    async def update_dashboard_metrics(self):
        """Update dashboard with latest security metrics"""
        try:
            # Get scan results
            scan_results = self._load_scan_results()
            
            # Prepare metrics
            metrics = {
                'id': f'metrics_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'type': 'security_metrics',
                'timestamp': datetime.utcnow().isoformat(),
                'scan_results': scan_results,
                'security_score': self._calculate_security_score(scan_results),
                'status': 'completed'
            }
            
            # Store in Cosmos DB
            try:
                self.container.upsert_item(metrics)
                print("✅ Dashboard metrics updated successfully")
            except Exception as e:
                print(f"Failed to store metrics in Cosmos DB: {str(e)}")
                raise
                
            return metrics
            
        except Exception as e:
            print(f"❌ Error updating dashboard metrics: {str(e)}")
            return {
                'id': f'metrics_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'type': 'security_metrics',
                'timestamp': datetime.utcnow().isoformat(),
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
        except FileNotFoundError:
            results['sast'] = {'metrics': {'high': 0, 'medium': 0, 'low': 0}}
        except json.JSONDecodeError:
            results['sast'] = {'metrics': {'high': 0, 'medium': 0, 'low': 0}}
            
        # Load dependency check results if available
        try:
            with open('safety-results.json', 'r') as f:
                results['dependencies'] = json.load(f)
        except FileNotFoundError:
            results['dependencies'] = []
        except json.JSONDecodeError:
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
        
        # Deduct for SAST findings
        sast_metrics = scan_results.get('sast', {}).get('metrics', {})
        score = base_score
        for severity, count in sast_metrics.items():
            if severity in deductions:
                score -= count * deductions[severity]
                
        # Deduct for dependency issues
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
        
        # Save metrics locally for debugging
        with open('dashboard_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
            
        print(f"Security Score: {metrics.get('security_score', 'N/A')}")
        
    except Exception as e:
        print(f"Failed to update dashboard: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())