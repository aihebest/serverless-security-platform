# infrastructure/get_connection_strings.py

import os
import json
import subprocess
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionStringRetriever:
    def __init__(self):
        load_dotenv()
        self.az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        self.load_resource_names()
        self.connection_strings = {}

    def load_resource_names(self):
        """Load resource names from JSON file"""
        with open('infrastructure/resource_names.json', 'r') as f:
            self.resources = json.load(f)
            logger.info("Resource names loaded successfully")

    def run_az_command(self, args):
        """Run Azure CLI command and return output"""
        try:
            cmd = [self.az_cmd] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout) if result.stdout.strip() else None
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            return None

    def get_cosmos_connection(self):
        """Get Cosmos DB connection string"""
        logger.info("Getting Cosmos DB connection string...")
        result = self.run_az_command([
            'cosmosdb', 'keys', 'list',
            '--name', self.resources['cosmos_db'],
            '--resource-group', self.resources['resource_group'],
            '--type', 'connection-strings'
        ])
        if result and result.get('connectionStrings'):
            self.connection_strings['COSMOS_DB_CONNECTION_STRING'] = result['connectionStrings'][0]['connectionString']
            logger.info("✓ Cosmos DB connection string retrieved")

    def get_signalr_connection(self):
        """Get SignalR connection string"""
        logger.info("Getting SignalR connection string...")
        result = self.run_az_command([
            'signalr', 'key', 'show',
            '--name', self.resources['signalr'],
            '--resource-group', self.resources['resource_group']
        ])
        if result:
            self.connection_strings['SIGNALR_CONNECTION_STRING'] = result.get('primaryConnectionString')
            logger.info("✓ SignalR connection string retrieved")

    def get_storage_connection(self):
        """Get Storage account connection string"""
        logger.info("Getting Storage account connection string...")
        result = self.run_az_command([
            'storage', 'account', 'show-connection-string',
            '--name', self.resources['storage'],
            '--resource-group', self.resources['resource_group']
        ])
        if result:
            self.connection_strings['STORAGE_CONNECTION_STRING'] = result.get('connectionString')
            logger.info("✓ Storage connection string retrieved")

    def get_app_insights_key(self):
        """Get Application Insights instrumentation key"""
        logger.info("Getting Application Insights instrumentation key...")
        result = self.run_az_command([
            'monitor', 'app-insights', 'component', 'show',
            '--app', self.resources['app_insights'],
            '--resource-group', self.resources['resource_group']
        ])
        if result:
            self.connection_strings['APPLICATIONINSIGHTS_CONNECTION_STRING'] = f"InstrumentationKey={result.get('instrumentationKey')}"
            logger.info("✓ Application Insights key retrieved")

    def update_env_file(self):
        """Update .env file with all connection strings"""
        # Get all connection strings
        self.get_cosmos_connection()
        self.get_signalr_connection()
        self.get_storage_connection()
        self.get_app_insights_key()

        # Add resource names
        self.connection_strings.update({
            'COSMOS_DB_NAME': self.resources['cosmos_db'],
            'SIGNALR_NAME': self.resources['signalr'],
            'STORAGE_ACCOUNT_NAME': self.resources['storage'],
            'FUNCTION_APP_NAME': self.resources['function_app'],
            'APP_INSIGHTS_NAME': self.resources['app_insights'],
            'RESOURCE_GROUP': self.resources['resource_group'],
            'COSMOS_DB_DATABASE_NAME': 'SecurityFindings',
            'COSMOS_DB_CONTAINER_NAME': 'SecurityScans'
        })

        # Create backup of existing .env if it exists
        if os.path.exists('.env'):
            os.rename('.env', '.env.backup')
            logger.info("Created backup of existing .env file")

        # Write new .env file
        with open('.env', 'w') as f:
            for key, value in self.connection_strings.items():
                f.write(f'{key}={value}\n')

        logger.info("✓ Environment file updated successfully!")
        return self.connection_strings

def main():
    try:
        retriever = ConnectionStringRetriever()
        configs = retriever.update_env_file()
        logger.info("Connection strings retrieved and saved successfully!")
    except Exception as e:
        logger.error(f"Failed to retrieve connection strings: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()