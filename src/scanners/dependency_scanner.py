# src/scanners/dependency_scanner.py

import asyncio
from typing import List, Dict
from datetime import datetime
import uuid
import aiohttp
from .base_scanner import BaseScanner, ScanResult
import json
import os

class DependencyScanner(BaseScanner):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.vuln_db_url = config.get('vulnerability_database_url')
        self.scan_depth = config.get('scan_depth', 'DEEP')
        
    async def validate_configuration(self) -> bool:
        if not self.vuln_db_url:
            self.logger.error("Vulnerability database URL not configured")
            return False
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.vuln_db_url}/health") as response:
                    return response.status == 200
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False

    async def scan_package(self, package_info: Dict) -> List[ScanResult]:
        results = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.vuln_db_url}/vulnerabilities",
                    params={'package': json.dumps(package_info)}
                ) as response:
                    if response.status == 200:
                        vulns = await response.json()
                        for vuln in vulns:
                            results.append(ScanResult(
                                scan_id=str(uuid.uuid4()),
                                timestamp=datetime.utcnow(),
                                severity=vuln['severity'],
                                finding_type='DEPENDENCY_VULNERABILITY',
                                description=vuln['description'],
                                affected_resource=f"{package_info['name']}@{package_info['version']}",
                                recommendation=vuln['recommendation'],
                                metadata={'cve_id': vuln.get('cve_id')}
                            ))
        except Exception as e:
            self.logger.error(f"Error scanning package {package_info['name']}: {str(e)}")
        return results

    async def scan(self) -> List[ScanResult]:
        results = []
        requirements_file = 'requirements.txt'
        
        if not os.path.exists(requirements_file):
            self.logger.error(f"Requirements file {requirements_file} not found")
            return results

        with open(requirements_file, 'r') as f:
            packages = f.readlines()

        scan_tasks = []
        for package in packages:
            if package.strip() and not package.startswith('#'):
                name, version = package.strip().split('==')
                scan_tasks.append(self.scan_package({
                    'name': name,
                    'version': version
                }))

        scan_results = await asyncio.gather(*scan_tasks)
        for result in scan_results:
            results.extend(result)

        return results