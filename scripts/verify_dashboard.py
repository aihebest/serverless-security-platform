# scripts/verify_dashboard.py
import os
import json
import asyncio
from datetime import datetime
from azure.cosmos import CosmosClient, exceptions

class DashboardMetricsProcessor:
    def __init__(self):
        try:
            connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING')
            if not connection_string:
                raise ValueError("COSMOS_DB_CONNECTION_STRING environment variable is not set")
            
            # Connect to existing database and container using your actual names
            print("Connecting to Cosmos DB...")
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            self.database = self.cosmos_client.get_database_client("SecurityScans")  # Your actual database name
            self.container = self.database.get_container_client("ScanResults")  # Your actual container name
            
            print("✅ Connected to Cosmos DB successfully")
            
        except Exception as e:
            print(f"Failed to connect to Cosmos DB: {str(e)}")
            raise

    async def update_dashboard_metrics(self):
        """Update dashboard with latest security metrics"""
        try:
            scan_id = f'scan_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}'
            
            # Prepare scan document
            scan_document = {
                'id': scan_id,
                'ResourceId': f'/subscriptions/5eeb3d1f-7dc7-4cf8-be96-9b979ea25792',  # Your subscription ID
                'ResourceName': 'security-scan-results-db',
                'ScanTime': datetime.utcnow().isoformat(),
                'Findings': self._load_scan_results(),
                '_rid': scan_id,
                '_self': f'/dbs/SecurityScans/colls/ScanResults/docs/{scan_id}',
                '_etag': f'\"{datetime.utcnow().timestamp()}\"',
                '_attachments': 'attachments/',
                '_ts': int(datetime.utcnow().timestamp())
            }
            
            # Store in Cosmos DB
            print("Storing scan results in Cosmos DB...")
            self.container.upsert_item(scan_document)
            print("✅ Scan results stored successfully")
            
            # Save locally for verification
            with open('scan_results.json', 'w') as f:
                json.dump(scan_document, f, indent=2)
                
            return scan_document
            
        except Exception as e:
            print(f"❌ Error storing scan results: {str(e)}")
            return {
                'id': scan_id,
                'status': 'failed',
                'error': str(e)
            }

    def _load_scan_results(self):
        """Load and process scan results files"""
        findings = []
        
        # Load SAST results
        try:
            with open('bandit-results.json', 'r') as f:
                sast_results = json.load(f)
                if sast_results.get('metrics', {}).get('high', 0) > 0:
                    findings.append({
                        'Severity': 'High',
                        'Description': 'High severity security issues found',
                        'Recommendation': 'Review and fix high severity security issues'
                    })
                if sast_results.get('metrics', {}).get('medium', 0) > 0:
                    findings.append({
                        'Severity': 'Medium',
                        'Description': 'Medium severity security issues found',
                        'Recommendation': 'Review and address medium severity issues'
                    })
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ No SAST results found: {str(e)}")
            
        # Load dependency check results
        try:
            with open('safety-results.json', 'r') as f:
                deps_results = json.load(f)
                for issue in deps_results:
                    findings.append({
                        'Severity': issue.get('severity', 'Low'),
                        'Description': f"Dependency issue: {issue.get('package', '')}",
                        'Recommendation': issue.get('advisory', 'Update dependency')
                    })
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ No dependency check results found: {str(e)}")
            
        return findings

async def main():
    try:
        print("Starting scan results update...")
        processor = DashboardMetricsProcessor()
        results = await processor.update_dashboard_metrics()
        print("Scan Update Complete")
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Failed to update scan results: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())