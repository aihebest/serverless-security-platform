# scripts/deploy.py

import os
import argparse
import json
import subprocess
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient

def load_config():
    """Load deployment configuration"""
    with open('infrastructure/deploy/azure-config.yaml', 'r') as f:
        return yaml.safe_load(f)

def setup_azure_resources(config):
    """Set up Azure resources using configuration"""
    credential = DefaultAzureCredential()
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    
    # Initialize clients
    resource_client = ResourceManagementClient(credential, subscription_id)
    web_client = WebSiteManagementClient(credential, subscription_id)
    
    # Ensure resource group exists
    resource_client.resource_groups.create_or_update(
        config['resourceGroup'],
        {'location': config['location']}
    )
    
    # Deploy ARM template
    template_path = 'infrastructure/arm-templates/azure-deploy.json'
    with open(template_path, 'r') as template_file:
        template = json.load(template_file)
        
    deployment_properties = {
        'mode': 'Incremental',
        'template': template,
        'parameters': {
            'functionAppName': {'value': config['services']['functionApp']['name']},
            'webAppName': {'value': config['services']['staticWebApp']['name']},
            'location': {'value': config['location']}
        }
    }
    
    return resource_client.deployments.begin_create_or_update(
        config['resourceGroup'],
        'deployment-{}'.format(int(time.time())),
        deployment_properties
    )

def deploy_function_app(config):
    """Deploy Function App code"""
    function_app_name = config['services']['functionApp']['name']
    
    # Build and package function app
    subprocess.run(['func', 'azure', 'functionapp', 'publish', function_app_name])

def deploy_static_web_app(config):
    """Deploy Static Web App"""
    web_app_name = config['services']['staticWebApp']['name']
    
    # Build web app
    subprocess.run(['npm', 'run', 'build'], cwd='src/dashboard')
    
    # Deploy to Azure
    subprocess.run([
        'az', 'staticwebapp', 'deploy',
        '--name', web_app_name,
        '--source', 'src/dashboard/build',
        '--token', os.getenv('AZURE_STATIC_WEB_APP_TOKEN')
    ])

def main():
    parser = argparse.ArgumentParser(description='Deploy Security Platform')
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Setup Azure resources
    setup_azure_resources(config)
    
    # Deploy Function App
    deploy_function_app(config)
    
    # Deploy Static Web App
    deploy_static_web_app(config)
    
    print('Deployment completed successfully!')

if __name__ == '__main__':
    main()