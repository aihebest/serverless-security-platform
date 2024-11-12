# infrastructure/deploy_azure_cli.py

import os
import subprocess
import json
import logging
import random
import string
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AzureDeployer:
    def __init__(self):
        load_dotenv('.env')
        self.resource_group = os.getenv('AZURE_FUNCTIONS_ENVIRONMENT', 'Production')
        self.location = 'westeurope'
        self.az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        self.timestamp = datetime.now().strftime("%Y%m%d")
        self.unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

    def generate_unique_name(self, base_name, max_length=24):
        """Generate a unique name for Azure resources"""
        # Remove special characters and spaces, convert to lowercase
        clean_base = ''.join(e for e in base_name if e.isalnum()).lower()
        # Ensure the name isn't too long
        name_prefix = clean_base[:max_length - len(self.unique_suffix) - 1]
        return f"{name_prefix}{self.unique_suffix}"

    def run_az_command(self, args, error_message="Command failed"):
        """Run Azure CLI command and handle output"""
        try:
            cmd = [self.az_cmd] + args
            logger.info(f"Running command: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                logger.error(f"Command failed with error: {process.stderr}")
                return None
            
            return process.stdout.strip()
            
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            return None

    def deploy_resources(self):
        """Deploy Azure resources"""
        try:
            # Generate unique names
            signalr_name = self.generate_unique_name("securityauto")
            storage_name = self.generate_unique_name("securitystorage")
            function_app_name = self.generate_unique_name("fasecurityautomation")
            cosmos_db_name = self.generate_unique_name("securitydb")
            app_insights_name = self.generate_unique_name("aisecurity")

            # Create resource group
            logger.info(f"Creating resource group: {self.resource_group}")
            self.run_az_command([
                'group', 
                'create',
                '--name', self.resource_group,
                '--location', self.location
            ])

            # Deploy App Insights
            logger.info(f"Deploying Application Insights: {app_insights_name}")
            self.run_az_command([
                'monitor', 
                'app-insights', 
                'component', 
                'create',
                '--app', app_insights_name,
                '--location', self.location,
                '--resource-group', self.resource_group,
                '--application-type', 'web'
            ])

            # Deploy Cosmos DB
            logger.info(f"Deploying Cosmos DB: {cosmos_db_name}")
            self.run_az_command([
                'cosmosdb', 
                'create',
                '--name', cosmos_db_name,
                '--resource-group', self.resource_group,
                '--kind', 'GlobalDocumentDB',
                '--default-consistency-level', 'Session'
            ])

            # Create Cosmos DB Database
            self.run_az_command([
                'cosmosdb', 
                'sql', 
                'database', 
                'create',
                '--account-name', cosmos_db_name,
                '--name', 'SecurityFindings',
                '--resource-group', self.resource_group
            ])

            # Deploy SignalR
            logger.info(f"Deploying SignalR: {signalr_name}")
            self.run_az_command([
                'signalr', 
                'create',
                '--name', signalr_name,
                '--resource-group', self.resource_group,
                '--sku', 'Standard_S1',
                '--service-mode', 'Default'
            ])

            # Create storage account
            logger.info(f"Creating storage account: {storage_name}")
            self.run_az_command([
                'storage', 
                'account', 
                'create',
                '--name', storage_name,
                '--resource-group', self.resource_group,
                '--location', self.location,
                '--sku', 'Standard_LRS'
            ])

            # Deploy Function App
            logger.info(f"Deploying Function App: {function_app_name}")
            self.run_az_command([
                'functionapp', 
                'create',
                '--name', function_app_name,
                '--storage-account', storage_name,
                '--resource-group', self.resource_group,
                '--consumption-plan-location', self.location,
                '--runtime', 'python',
                '--runtime-version', '3.9',
                '--functions-version', '4',
                '--os-type', 'Linux'
            ])

            # Save the generated names to a file for reference
            with open('deployed_resources.txt', 'w') as f:
                f.write(f"""
Deployed Azure Resources:
------------------------
Resource Group: {self.resource_group}
SignalR: {signalr_name}
Storage Account: {storage_name}
Function App: {function_app_name}
Cosmos DB: {cosmos_db_name}
Application Insights: {app_insights_name}
                """)

            logger.info("All resources deployed successfully!")
            logger.info("Resource names saved to deployed_resources.txt")
            return True

        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            return False

def main():
    deployer = AzureDeployer()
    success = deployer.deploy_resources()
    if not success:
        logger.error("Deployment failed")
        exit(1)
    logger.info("Deployment completed successfully")

if __name__ == "__main__":
    main()