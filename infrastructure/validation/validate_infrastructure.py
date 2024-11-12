# infrastructure/validation/validate_infrastructure.py
import os
import yaml
import json
import logging
from datetime import datetime

class SimpleInfrastructureValidator:
    def __init__(self):
        self.logger = self._setup_logging()
        self.results = {
            "resources": [],
            "overall_status": "pending",
            "timestamp": datetime.now().isoformat()
        }

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('infrastructure_validation.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def _load_config(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'validation-config.yaml')
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            raise

    def _load_current_resources(self):
        try:
            resources_path = os.path.join(os.path.dirname(__file__), 'current_resources.json')
            with open(resources_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load current resources: {str(e)}")
            raise

    def validate_resources(self):
        """Validate resources against requirements"""
        self.logger.info("Starting resource validation...")
        config = self._load_config()
        current_resources = self._load_current_resources()
        
        for required in config['resources']:
            self._validate_single_resource(required, current_resources)

    def _validate_single_resource(self, required, current_resources):
        """Validate a single resource"""
        resource_name = required['name']
        self.logger.info(f"Validating resource: {resource_name}")
        
        # Find matching resource
        matching = [r for r in current_resources if r['name'] == resource_name]
        
        if not matching:
            result = {
                "name": resource_name,
                "type": required['type'],
                "exists": False,
                "status": "Missing",
                "details": "Resource not found"
            }
        else:
            current = matching[0]
            properties_valid = self._validate_properties(required, current)
            result = {
                "name": resource_name,
                "type": required['type'],
                "exists": True,
                "status": current.get('provisioningState', 'Unknown'),
                "properties_valid": properties_valid,
                "details": "Properties match" if properties_valid else "Property mismatch"
            }
        
        self.results["resources"].append(result)
        self.logger.info(f"Resource {resource_name}: {result['status']}")

    def _validate_properties(self, required, current):
        """Compare required properties with current resource"""
        try:
            required_props = required.get('required_properties', {})
            
            # Check basic properties
            for key in ['kind', 'location']:
                if key in required_props and current.get(key) != required_props[key]:
                    self.logger.warning(f"Property mismatch for {current['name']}: {key}")
                    return False
            
            # Check SKU if specified
            if 'sku' in required_props:
                current_sku = current.get('sku', {})
                required_sku = required_props['sku']
                if not self._compare_sku(required_sku, current_sku):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating properties: {str(e)}")
            return False

    def _compare_sku(self, required_sku, current_sku):
        """Compare SKU properties"""
        if not current_sku:
            return False
        
        for key in ['tier', 'name']:
            if key in required_sku and required_sku[key] != current_sku.get(key):
                self.logger.warning(f"SKU mismatch: {key}")
                return False
        return True

    def run_validation(self):
        """Run the validation process"""
        try:
            self.logger.info("Starting validation...")
            self.validate_resources()
            
            # Determine overall status
            has_failures = any(
                not r['exists'] or 
                (r['exists'] and not r.get('properties_valid', False))
                for r in self.results['resources']
            )
            
            self.results['overall_status'] = "FAILED" if has_failures else "PASSED"
            
            # Save results
            self._save_results()
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            raise

    def _save_results(self):
        """Save validation results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validation_results_{timestamp}.json"
        output_path = os.path.join(os.path.dirname(__file__), filename)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"Results saved to {output_path}")

def main():
    validator = SimpleInfrastructureValidator()
    results = validator.run_validation()
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()