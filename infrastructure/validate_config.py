# infrastructure/validate_config.py

import os
import json
import subprocess
import logging
from dotenv import load_dotenv
import time
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConfigValidator:
    def __init__(self):
        load_dotenv()
        self.az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        self.load_resource_names()

    def load_resource_names(self):
        """Load resource names from JSON file"""
        try:
            resource_names_path = os.path.join('infrastructure', 'resource_names.json')
            logger.info(f"Loading resource names from: {resource_names_path}")
            
            with open(resource_names_path, 'r') as f:
                self.resources = json.load(f)
                logger.info("Resource names loaded successfully")
                logger.info(f"Resources: {json.dumps(self.resources, indent=2)}")
        except FileNotFoundError:
            logger.error("Resource names file not found!")
            raise

    def run_az_command(self, args):
        """Run Azure CLI command and return output"""
        try:
            cmd = [self.az_cmd] + args
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Command failed: {result.stderr}")
                return None
                
            try:
                return json.loads(result.stdout) if result.stdout.strip() else None
            except json.JSONDecodeError:
                return result.stdout.strip()
                
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return None

    def validate_cosmos_db(self):
        """Validate Cosmos DB exists and if not, create it"""
        try:
            cosmos_db_name = self.resources['cosmos_db']
            logger.info(f"Validating Cosmos DB: {cosmos_db_name}")
            
            # First try to list all Cosmos DB accounts
            list_result = self.run_az_command([
                'cosmosdb', 'list',
                '--resource-group', self.resources['resource_group']
            ])
            
            if list_result:
                existing_accounts = [acc['name'] for acc in list_result]
                logger.info(f"Found Cosmos DB accounts: {existing_accounts}")
                
                if cosmos_db_name not in existing_accounts:
                    logger.info(f"Cosmos DB {cosmos_db_name} not found, creating...")
                    # Create Cosmos DB account
                    create_result = self.run_az_command([
                        'cosmosdb', 'create',
                        '--name', cosmos_db_name,
                        '--resource-group', self.resources['resource_group'],
                        '--kind', 'GlobalDocumentDB',
                        '--default-consistency-level', 'Session',
                        '--enable-free-tier', 'true',
                        '--locations', 'regionName=westeurope failoverPriority=0'
                    ])
                    
                    if not create_result:
                        logger.error("Failed to create Cosmos DB account")
                        return False
                    
                    logger.info("Cosmos DB account created, creating database...")
                    
                # Create database if it doesn't exist
                db_create_result = self.run_az_command([
                    'cosmosdb', 'sql', 'database', 'create',
                    '--account-name', cosmos_db_name,
                    '--name', 'SecurityFindings',
                    '--resource-group', self.resources['resource_group']
                ])
                
                if db_create_result:
                    logger.info("Database created/verified")
                    
                    # Create container if it doesn't exist
                    container_result = self.run_az_command([
                        'cosmosdb', 'sql', 'container', 'create',
                        '--account-name', cosmos_db_name,
                        '--database-name', 'SecurityFindings',
                        '--name', 'SecurityScans',
                        '--partition-key-path', '/scanId',
                        '--resource-group', self.resources['resource_group']
                    ])
                    
                    if container_result:
                        logger.info("✓ Cosmos DB validated and configured successfully")
                        return True
            
            logger.error("Failed to validate or create Cosmos DB")
            return False
            
        except Exception as e:
            logger.error(f"Cosmos DB validation failed: {str(e)}")
            return False

    def validate_signalr(self):
        """Validate SignalR service exists and is accessible"""
        try:
            signalr_name = self.resources['signalr']
            logger.info(f"Validating SignalR: {signalr_name}")
            
            result = self.run_az_command([
                'signalr', 'show',
                '--name', signalr_name,
                '--resource-group', self.resources['resource_group']
            ])
            
            if result:
                logger.info("✓ SignalR service validated successfully")
                return True
                
            logger.error(f"SignalR {signalr_name} not found or not accessible")
            return False
            
        except Exception as e:
            logger.error(f"SignalR validation failed: {str(e)}")
            return False

    def validate_storage(self):
        """Validate Storage account exists and is accessible"""
        try:
            storage_name = self.resources['storage']
            logger.info(f"Validating Storage Account: {storage_name}")
            
            result = self.run_az_command([
                'storage', 'account', 'show',
                '--name', storage_name,
                '--resource-group', self.resources['resource_group']
            ])
            
            if result:
                logger.info("✓ Storage account validated successfully")
                return True
                
            logger.error(f"Storage account {storage_name} not found or not accessible")
            return False
            
        except Exception as e:
            logger.error(f"Storage validation failed: {str(e)}")
            return False

    def validate_function_app(self):
        """Validate Function App exists and is accessible"""
        try:
            function_app_name = self.resources['function_app']
            logger.info(f"Validating Function App: {function_app_name}")
            
            # List all function apps
            logger.info("Listing function apps...")
            list_result = self.run_az_command([
                'functionapp', 'list',
                '--resource-group', self.resources['resource_group']
            ])
            
            if list_result:
                available_apps = [app['name'] for app in list_result]
                logger.info(f"Available Function Apps: {available_apps}")
                
                if function_app_name in available_apps:
                    logger.info("✓ Function App exists")
                    return True
                else:
                    logger.info(f"Function App {function_app_name} not found, attempting to create with consumption plan...")
                    create_result = self.run_az_command([
                        'functionapp', 'create',
                        '--name', function_app_name,
                        '--storage-account', self.resources['storage'],
                        '--resource-group', self.resources['resource_group'],
                        '--consumption-plan-location', 'westeurope',  # or your preferred region
                        '--runtime', 'python',
                        '--runtime-version', '3.9',
                        '--functions-version', '4',
                        '--os-type', 'linux'
                    ])
                    
                    if create_result:
                        logger.info("✓ Function App created successfully")
                        return True
                    else:
                        logger.error("Failed to create Function App")
                        return False
            
            logger.error("Failed to validate or create Function App")
            return False
            
        except Exception as e:
            logger.error(f"Function App validation/creation failed: {str(e)}")
            return False

    def validate_app_insights(self):
        """Validate Application Insights exists and is accessible"""
        try:
            app_insights_name = self.resources['app_insights']
            logger.info(f"Validating Application Insights: {app_insights_name}")
            
            result = self.run_az_command([
                'monitor', 'app-insights', 'component', 'show',
                '--app', app_insights_name,
                '--resource-group', self.resources['resource_group']
            ])
            
            if result:
                logger.info("✓ Application Insights validated successfully")
                return True
                
            logger.error(f"Application Insights {app_insights_name} not found or not accessible")
            return False
            
        except Exception as e:
            logger.error(f"Application Insights validation failed: {str(e)}")
            return False
        
    def retry_operation(self, operation, max_attempts=3, delay=5):
        """Retry an operation with exponential backoff"""
        for attempt in range(max_attempts):
            try:
                result = operation()
                if result:
                    return result
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
            if attempt < max_attempts - 1:
                wait_time = delay * (2 ** attempt)
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        return False

    def validate_all(self):
        """Validate all Azure resources with retry"""
        validations = {
            'Cosmos DB': lambda: self.retry_operation(self.validate_cosmos_db),
            'SignalR': lambda: self.retry_operation(self.validate_signalr),
            'Storage': lambda: self.retry_operation(self.validate_storage),
            'Function App': lambda: self.retry_operation(self.validate_function_app),
            'Application Insights': lambda: self.retry_operation(self.validate_app_insights)
        }
        
        results = {}
        for service, validation in validations.items():
            logger.info(f"\nValidating {service}...")
            results[service] = validation()
        
        all_valid = all(results.values())
        
        if all_valid:
            logger.info("\n✅ All configurations validated successfully!")
        else:
            logger.error("\n❌ Some validations failed:")
            for service, status in results.items():
                logger.info(f"{service}: {'✓' if status else '✗'}")
        
        return all_valid, results

def main():
    try:
        validator = ConfigValidator()
        success, results = validator.validate_all()
        if not success:
            logger.error("Validation failed")
            exit(1)
        logger.info("All validations completed successfully")
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()