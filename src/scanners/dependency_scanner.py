# src/scanners/dependency_scanner.py
from typing import Dict, List
import logging
from datetime import datetime, UTC
from .base_scanner import BaseScanner

class DependencyScanner(BaseScanner):
    def __init__(self):
        self.known_vulnerabilities = {
            'requests<2.28.0': {'severity': 'high', 'description': 'CVE-2023-XXXX'},
            'django<3.2': {'severity': 'critical', 'description': 'Multiple CVEs'}
        }

    async def scan(self, requirements_file: str) -> Dict:
        try:
            dependencies = self._parse_requirements(requirements_file)
            vulnerabilities = []
            
            for dep in dependencies:
                if await self._check_vulnerability(dep):
                    vulnerabilities.append({
                        'package': dep['name'],
                        'version': dep['version'],
                        'severity': 'high',
                        'details': f"Vulnerable version of {dep['name']} detected"
                    })
                    
            return self.generate_report(vulnerabilities)
        except Exception as e:
            logging.error(f"Dependency scan failed: {str(e)}")
            return {
                'timestamp': datetime.now(UTC).isoformat(),
                'error': str(e),
                'scan_status': 'failed'
            }

    def _parse_requirements(self, file_path: str) -> List[Dict]:
        dependencies = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '==' in line:
                        name, version = line.strip().split('==')
                        dependencies.append({
                            'name': name.strip(),
                            'version': version.strip()
                        })
        return dependencies

    async def _check_vulnerability(self, dependency: Dict) -> bool:
        dep_str = f"{dependency['name']}<{dependency['version']}"
        return dep_str in self.known_vulnerabilities