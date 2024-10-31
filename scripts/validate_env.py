import sys
import subprocess
import json
from typing import Dict, List

class EnvironmentValidator:
    def __init__(self):
        self.required_tools = {
            'python': '3.9',
            'az': '2.0',
            'terraform': '1.0',
            'node': '14.0'
        }
        self.results = []

    def check_tool_version(self, tool: str, min_version: str) -> Dict:
        """Check if required tool is installed and meets minimum version"""
        try:
            if tool == 'python':
                version = sys.version.split()[0]
            else:
                result = subprocess.run([tool, '--version'], 
                                     capture_output=True, 
                                     text=True)
                version = result.stdout.split()[1]
            
            return {
                'tool': tool,
                'installed': True,
                'version': version,
                'meets_minimum': self._compare_versions(version, min_version),
                'minimum_required': min_version
            }
        except Exception as e:
            return {
                'tool': tool,
                'installed': False,
                'error': str(e)
            }

    def validate_environment(self) -> Dict:
        """Run all environment validation checks"""
        for tool, min_version in self.required_tools.items():
            result = self.check_tool_version(tool, min_version)
            self.results.append(result)

        return {
            'all_requirements_met': all(r.get('meets_minimum', False) 
                                     for r in self.results),
            'details': self.results
        }

    def _compare_versions(self, current: str, minimum: str) -> bool:
        """Compare version strings"""
        current_parts = [int(x) for x in current.split('.')]
        minimum_parts = [int(x) for x in minimum.split('.')]
        return current_parts >= minimum_parts

if __name__ == "__main__":
    validator = EnvironmentValidator()
    results = validator.validate_environment()
    print(json.dumps(results, indent=2))