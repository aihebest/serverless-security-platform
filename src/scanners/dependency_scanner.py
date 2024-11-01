# src/scanners/dependency_scanner.py
import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone
from .base_scanner import BaseScanner

class DependencyScanner(BaseScanner):
    def __init__(self):
        super().__init__()
        # Example vulnerability database (in production, you'd use a real security database)
        self.vulnerability_db = {
            'django': {
                '2.2': {'severity': 'high', 'vulnerabilities': ['CVE-2021-33203']},
                '3.0': {'severity': 'medium', 'vulnerabilities': ['CVE-2021-35042']},
            },
            'requests': {
                '2.25': {'severity': 'low', 'vulnerabilities': ['CVE-2021-29476']},
            },
            'flask': {
                '1.1.2': {'severity': 'medium', 'vulnerabilities': ['CVE-2021-28091']},
            }
        }

    async def scan(self, requirements_file: str) -> dict:
        """Scan Python dependencies for known vulnerabilities"""
        try:
            dependencies = await self._parse_requirements(requirements_file)
            scan_results = []
            
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self._check_dependency(session, dep) 
                    for dep in dependencies
                ]
                scan_results = await asyncio.gather(*tasks)

            vulnerabilities = [
                result for result in scan_results 
                if result is not None
            ]

            # Calculate risk score based on vulnerabilities
            risk_score = self._calculate_risk_score(vulnerabilities)
            
            return self.generate_report({
                'scan_id': self._generate_scan_id(vulnerabilities),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'dependencies_scanned': len(dependencies),
                'vulnerabilities_found': len(vulnerabilities),
                'risk_score': risk_score,
                'findings': vulnerabilities,
                'scan_type': 'dependency',
                'scan_status': 'completed'
            })

        except Exception as e:
            return self.generate_report({
                'scan_status': 'failed',
                'error': str(e),
                'scan_type': 'dependency'
            })

    async def _parse_requirements(self, file_path: str) -> list:
        """Parse requirements.txt file"""
        dependencies = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            name, version = line.split('==')
                            dependencies.append({
                                'name': name.strip(),
                                'version': version.strip()
                            })
        except Exception as e:
            print(f"Error parsing requirements: {e}")
        return dependencies

    async def _check_dependency(self, session: aiohttp.ClientSession, dependency: dict) -> dict:
        """Check a single dependency for vulnerabilities"""
        name = dependency['name']
        version = dependency['version']

        # Check local vulnerability database
        if name in self.vulnerability_db:
            for vuln_version, details in self.vulnerability_db[name].items():
                if self._is_vulnerable_version(version, vuln_version):
                    return {
                        'dependency': name,
                        'installed_version': version,
                        'vulnerability': {
                            'severity': details['severity'],
                            'cves': details['vulnerabilities'],
                            'description': f"Known vulnerabilities in {name}=={version}"
                        }
                    }

        # Optional: Check PyPI for package info
        try:
            async with session.get(f"https://pypi.org/pypi/{name}/json") as response:
                if response.status == 200:
                    data = await response.json()
                    releases = data.get('releases', {})
                    latest_version = max(releases.keys(), default=version)
                    if version != latest_version:
                        return {
                            'dependency': name,
                            'installed_version': version,
                            'vulnerability': {
                                'severity': 'info',
                                'description': f"Update available: {latest_version}"
                            }
                        }
        except Exception as e:
            print(f"Error checking PyPI for {name}: {e}")

        return None

    def _is_vulnerable_version(self, installed: str, vulnerable: str) -> bool:
        """Compare versions to determine if installed version is vulnerable"""
        installed_parts = [int(p) for p in installed.split('.')]
        vulnerable_parts = [int(p) for p in vulnerable.split('.')]
        
        return installed_parts <= vulnerable_parts

    def _calculate_risk_score(self, vulnerabilities: list) -> float:
        """Calculate risk score based on vulnerabilities"""
        if not vulnerabilities:
            return 100.0

        severity_weights = {
            'critical': 10.0,
            'high': 7.5,
            'medium': 5.0,
            'low': 2.5,
            'info': 0.5
        }

        total_weight = sum(
            severity_weights.get(v['vulnerability']['severity'], 0)
            for v in vulnerabilities
        )

        max_possible_weight = len(vulnerabilities) * severity_weights['critical']
        risk_score = 100 * (1 - (total_weight / max_possible_weight))
        
        return round(max(0.0, min(100.0, risk_score)), 2)