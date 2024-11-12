# infrastructure/verify_connections.py

import os
import asyncio
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
from azure.monitor.opentelemetry import configure_azure_monitor
import aiohttp
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionTester:
    def __init__(self):
        load_dotenv()
        self.results = {}

    async def test_cosmos_db(self):
        """Test Cosmos DB connection"""
        try:
            connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING')
            client = CosmosClient.from_connection_string(connection_string)
            
            # Test database and container access
            database = client.get_database_client(os.getenv('COSMOS_DB_DATABASE_NAME'))
            container = database.get_container_client(os.getenv('COSMOS_DB_CONTAINER_NAME'))
            
            # Try a simple operation
            await container.read()
            
            self.results['cosmos_db'] = "✓ Connected"
            logger.info("Cosmos DB connection successful")
            return True
        except Exception as e:
            self.results['cosmos_db'] = f"✗ Failed: {str(e)}"
            logger.error(f"Cosmos DB connection failed: {str(e)}")
            return False

    async def test_signalr(self):
        """Test SignalR connection"""
        try:
            connection_string = os.getenv('SIGNALR_CONNECTION_STRING')
            # Extract endpoint from connection string
            endpoint = dict(item.split('=') for item in connection_string.split(';'))['Endpoint']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{endpoint}/api/v1/health") as response:
                    if response.status == 200:
                        self.results['signalr'] = "✓ Connected"
                        logger.info("SignalR connection successful")
                        return True
                        
            self.results['signalr'] = "✗ Failed to connect"
            return False
        except Exception as e:
            self.results['signalr'] = f"✗ Failed: {str(e)}"
            logger.error(f"SignalR connection failed: {str(e)}")
            return False

    def test_storage(self):
        """Test Storage account connection"""
        try:
            connection_string = os.getenv('STORAGE_CONNECTION_STRING')
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Try to list containers
            containers = list(blob_service_client.list_containers(max_results=1))
            
            self.results['storage'] = "✓ Connected"
            logger.info("Storage account connection successful")
            return True
        except Exception as e:
            self.results['storage'] = f"✗ Failed: {str(e)}"
            logger.error(f"Storage account connection failed: {str(e)}")
            return False

    def test_app_insights(self):
        """Test Application Insights configuration"""
        try:
            connection_string = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
            configure_azure_monitor(connection_string=connection_string)
            
            self.results['app_insights'] = "✓ Configured"
            logger.info("Application Insights configuration successful")
            return True
        except Exception as e:
            self.results['app_insights'] = f"✗ Failed: {str(e)}"
            logger.error(f"Application Insights configuration failed: {str(e)}")
            return False

    async def verify_all_connections(self):
        """Verify all connections"""
        tasks = [
            self.test_cosmos_db(),
            self.test_signalr(),
        ]
        
        # Add synchronous tests
        self.test_storage()
        self.test_app_insights()
        
        await asyncio.gather(*tasks)
        
        # Print results
        print("\nConnection Test Results:")
        print("------------------------")
        for service, result in self.results.items():
            print(f"{service}: {result}")
            
        return all(not str(result).startswith('✗') for result in self.results.values())

async def main():
    tester = ConnectionTester()
    success = await tester.verify_all_connections()
    if not success:
        logger.error("Some connections failed!")
        exit(1)
    logger.info("All connections verified successfully!")

if __name__ == "__main__":
    asyncio.run(main())