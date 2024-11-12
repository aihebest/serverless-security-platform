# infrastructure/deploy_azure.py

import os
import sys
import logging
import asyncio
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.signalr import SignalRManagementClient
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityPlatformDeployer:
    def __init__(self):
        load_dotenv('.env')
        self.credential = DefaultAzureCredential()
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = os.getenv('AZURE_FUNCTIONS_ENVIRONMENT', 'Production')
        self.location = 'westeurope'  # or your preferred region

        # Initialize Azure clients
        self.init_azure_clients()

    def init_azure_clients(self):
        """Initialize Azure management clients"""
        self.resource_client = ResourceManagementClient(
            self.credential, 
            self.subscription_id
        )
        self.web_client = WebSiteManagementClient(
            self.credential, 
            self.subscription_id
        )
        self.cosmos_client = CosmosDBManagementClient(
            self.credential, 
            self.subscription_id
        )
        self.signalr_client = SignalRManagementClient(
            self.credential, 
            self.subscription_id
        )
        self.insights_client = ApplicationInsightsManagementClient(
            self.credential, 
            self.subscription_id
        )

    async def deploy_resources(self):
        """Deploy all Azure resources"""
        try:
            # Create resource group
            logger.info("Creating resource group...")
            await self.create_resource_group()

            # Deploy Application Insights
            logger.info("Deploying Application Insights...")
            app_insights = await self.deploy_app_insights()

            # Deploy Cosmos DB
            logger.info("Deploying Cosmos DB...")
            cosmos_db = await self.deploy_cosmos_db()

            # Deploy SignalR
            logger.info("Deploying SignalR...")
            signalr = await self.deploy_signalr()

            # Deploy Function App
            logger.info("Deploying Function App...")
            function_app = await self.deploy_function_app(app_insights.instrumentation_key)

            # Deploy Static Web App
            logger.info("Deploying Static Web App...")
            static_web_app = await self.deploy_static_web_app()

            logger.info("All resources deployed successfully!")
            return True

        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            return False

    async def create_resource_group(self):
        """Create or update resource group"""
        return self.resource_client.resource_groups.create_or_update(
            self.resource_group,
            {"location": self.location}
        )

    async def deploy_app_insights(self):
        """Deploy Application Insights"""
        return self.insights_client.components.create_or_update(
            self.resource_group,
            os.getenv('APP_INSIGHTS_NAME'),
            {
                "location": self.location,
                "kind": "web",
                "application_type": "web"
            }
        )

    async def deploy_cosmos_db(self):
        """Deploy Cosmos DB account and configure containers"""
        # Create Cosmos DB account
        cosmos_account = self.cosmos_client.database_accounts.begin_create_or_update(
            self.resource_group,
            os.getenv('COSMOS_DB_DATABASE_NAME'),
            {
                "location": self.location,
                "database_account_offer_type": "Standard",
                "locations": [{"location_name": self.location}],
                "consistency_policy": {
                    "default_consistency_level": "Session"
                }
            }
        ).result()

        # Get connection keys
        keys = self.cosmos_client.database_accounts.list_keys(
            self.resource_group,
            os.getenv('COSMOS_DB_DATABASE_NAME')
        )

        # Configure database and container
        cosmos_client = CosmosClient(
            cosmos_account.document_endpoint,
            keys.primary_master_key
        )

        database = cosmos_client.create_database_if_not_exists(
            os.getenv('COSMOS_DB_DATABASE_NAME')
        )

        database.create_container_if_not_exists(
            id=os.getenv('COSMOS_DB_CONTAINER_NAME'),
            partition_key='/scanId'
        )

        return cosmos_account

    async def deploy_signalr(self):
        """Deploy SignalR service"""
        return self.signalr_client.signal_r.begin_create_or_update(
            self.resource_group,
            "SecurityAuto",
            {
                "location": self.location,
                "sku": {
                    "name": "Standard_S1",
                    "capacity": 1
                },
                "features": [
                    {
                        "flag": "ServiceMode",
                        "value": os.getenv('SIGNALR_SERVICE_MODE')
                    }
                ]
            }
        ).result()

    async def deploy_function_app(self, app_insights_key):
        """Deploy Function App"""
        # Create App Service Plan
        service_plan = self.web_client.app_service_plans.begin_create_or_update(
            self.resource_group,
            "asp-security-automation",
            {
                "location": self.location,
                "sku": {"name": "Y1", "tier": "Dynamic"},
                "kind": "functionapp"
            }
        ).result()

        # Create Function App
        return self.web_client.web_apps.begin_create_or_update(
            self.resource_group,
            os.getenv('AZURE_FUNCTION_APP_NAME'),
            {
                "location": self.location,
                "kind": "functionapp",
                "site_config": {
                    "python_version": "3.9",
                    "app_settings": [
                        {"name": "FUNCTIONS_WORKER_RUNTIME", "value": "python"},
                        {"name": "WEBSITE_RUN_FROM_PACKAGE", "value": "1"},
                        {"name": "APPINSIGHTS_INSTRUMENTATIONKEY", "value": app_insights_key},
                        {"name": "FUNCTION_APP_SCALE_LIMIT", "value": os.getenv('FUNCTION_APP_SCALE_LIMIT')},
                    ]
                }
            }
        ).result()

    async def deploy_static_web_app(self):
        """Deploy Static Web App"""
        return self.web_client.static_sites.begin_create_or_update_static_site(
            self.resource_group,
            os.getenv('STATIC_WEBSITE_ENABLED'),
            {
                "location": self.location,
                "sku": {"name": "Standard"},
                "repository_url": "",  # Will be configured later with GitHub
                "branch": "main",
                "repository_token": None,  # Will be configured later
                "build_properties": {
                    "api_location": os.getenv('API_LOCATION'),
                    "app_location": os.getenv('APP_LOCATION'),
                    "output_location": os.getenv('OUTPUT_LOCATION')
                }
            }
        ).result()

async def main():
    deployer = SecurityPlatformDeployer()
    success = await deployer.deploy_resources()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())