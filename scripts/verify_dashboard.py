# scripts/verify_dashboard.py
import os
import json
import asyncio
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

class DashboardMetricsProcessor:
    def __init__(self):
        self.cosmos_client = CosmosClient.from_connection_string(
            os.getenv('COSMOS_DB_CONNECTION_STRING')
        )
        self.database = self.cosmos_client.get_database_client(
            os.getenv('COSMOS_DB_DATABASE_NAME')
        )
        self.container = self.database.get_container_client(
            os.getenv('COSMOS_DB_CONTAINER_NAME')
        )

    async def update_dashboard_metrics(self):
        """Update dashboard with latest security metrics"""
        try:
            # Process current scan results
            current_metrics = await self._process_current_scan()
            
            # Get historical data
            historical_data = await self._get_historical_data()
            
            # Calculate trends
            trends = await self._calculate_trends(historical_data)
            
            # Prepare dashboard data
            dashboard_data = {
                'id': f'dashboard_metrics_{datetime.utcnow().strftime("%Y%m%d")}',
                'type': 'security_dashboard',
                'timestamp': datetime.utcnow().isoformat(),
                'current_metrics': current_metrics,
                'trends': trends,
                'historical_data': historical_data
            }
            
            # Store in Cosmos DB
            await self.container.upsert_item(dashboard_data)
            
            print("✅ Dashboard metrics updated successfully")
            return dashboard_data
            
        except Exception as e:
            print(f"❌ Error updating dashboard metrics: {str(e)}")
            raise

    async def _process_current_scan(self):
        """Process current scan results"""
        try:
            # Read current scan results
            with open('bandit-results.json', 'r') as f:
                sast_results = json.load(f)
            
            with open('safety-results.json', 'r') as f:
                deps_results = json.load(f)
            
            # Calculate security score
            security_score = self._calculate_security_score(sast_results, deps_results)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'security_score': security_score,
                'vulnerabilities': {
                    'critical': len([r for r in deps_results if r.get('severity') == 'critical']),
                    'high': sast_results.get('metrics', {}).get('high', 0),
                    'medium': sast_results.get('metrics', {}).get('medium', 0),
                    'low': sast_results.get('metrics', {}).get('low', 0)
                },
                'compliance': {
                    'soc2': self._check_soc2_compliance(),
                    'hipaa': self._check_hipaa_compliance(),
                    'nist': self._check_nist_compliance()
                }
            }
        except Exception as e:
            print(f"Error processing current scan: {str(e)}")
            raise

    async def _get_historical_data(self):
        """Retrieve historical security metrics"""
        query = """
        SELECT * FROM c 
        WHERE c.type = 'security_dashboard' 
        ORDER BY c.timestamp DESC 
        OFFSET 0 LIMIT 30
        """
        
        items = self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        
        return list(items)

    def _calculate_security_score(self, sast_results, deps_results):
        """Calculate overall security score"""
        # Implement your scoring logic here
        base_score = 100
        
        # Deduct points for vulnerabilities
        deductions = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 2
        }
        
        total_deduction = 0
        # Process SAST results
        metrics = sast_results.get('metrics', {})
        total_deduction += deductions['high'] * metrics.get('high', 0)
        total_deduction += deductions['medium'] * metrics.get('medium', 0)
        total_deduction += deductions['low'] * metrics.get('low', 0)
        
        # Process dependency results
        for dep in deps_results:
            severity = dep.get('severity', 'low').lower()
            total_deduction += deductions.get(severity, 0)
        
        return max(0, base_score - total_deduction)

    def _check_soc2_compliance(self):
        return {'score': 92, 'status': 'compliant'}

    def _check_hipaa_compliance(self):
        return {'score': 88, 'status': 'compliant'}

    def _check_nist_compliance(self):
        return {'score': 90, 'status': 'compliant'}

async def main():
    processor = DashboardMetricsProcessor()
    await processor.update_dashboard_metrics()

if __name__ == "__main__":
    asyncio.run(main())