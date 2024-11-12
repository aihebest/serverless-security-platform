# infrastructure/resource_names.py

import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_deployed_resource_names():
    """Get resource names from deployment"""
    # Define resource names based on your successful validations
    resource_names = {
        'cosmos_db': 'securitydbrrj0x',        # ✓ Validated
        'signalr': 'securityautorrj0x',        # ✓ Validated
        'storage': 'securitystoragerrj0x',     # ✓ Validated
        'function_app': 'fasecurityautomatinrrj0x',  # Using the correct function app name
        'app_insights': 'aisecurityrrj0x',     # ✓ Validated
        'resource_group': 'Production'
    }
    
    # Save to a JSON file in the infrastructure directory
    try:
        with open('infrastructure/resource_names.json', 'w') as f:
            json.dump(resource_names, f, indent=2)
        logger.info(f"Resource names saved to infrastructure/resource_names.json")
        
        # Log the resources
        logger.info("Resource Names:")
        for key, value in resource_names.items():
            logger.info(f"{key}: {value}")
            
    except Exception as e:
        logger.error(f"Error saving resource names: {str(e)}")
        raise
    
    return resource_names

def main():
    try:
        resource_names = get_deployed_resource_names()
        logger.info("Resource names generated and saved successfully")
    except Exception as e:
        logger.error(f"Failed to generate resource names: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()