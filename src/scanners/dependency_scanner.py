# src/scanners/dependency_scanner.py

from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
import logging
from datetime import datetime
from ..scanners.base_scanner import BaseScanner, SecurityFinding

logger = logging.getLogger(__name__)

class DependencyVulnerability:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.title = data.get('title')
        self.description = data.get('description')
        self.severity = data.get('severity', 'MEDIUM')
        self.package_name = data.get('package_name')
        self.version = data.get('version')
        self.fixed_version = data.get('fixed_version')
        self.references = data.get('references', [])

class DependencyScanner(BaseScanner):
    def __init__(self):
        super().__init__(scan_type="dependency")
        self.nvd_api_key = os.getenv('NVD_API_KEY')
        self.osv_base_url = "https://api.osv.dev/v1/query"

    async def scan(self, dependencies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Scan dependencies for vulnerabilities"""
        try:
            tasks = []
            for dep in dependencies:
                tasks.append(self.check_dependency(dep))
            
            await asyncio.gather(*tasks)
            return self.get_scan_results()
            
        except Exception as e:
            logger.error(f"Dependency scan failed: {str(e)}")
            raise

    async def check_dependency(self, dependency: Dict[str, str]):
        """Check a single dependency for vulnerabilities"""
        name = dependency.get('name')
        version = dependency.get('version')
        
        if not name or not version:
            logger.warning(f"Invalid dependency format: {dependency}")
            return
        
        try:
            # Check OSV database
            osv_vulns = await self.check_osv_database(name, version)
            
            # Check NVD database if API key is available
            nvd_vulns = []
            if self.nvd_api_key:
                nvd_vulns = await self.check_nvd_database(name, version)
            
            # Combine and deduplicate vulnerabilities
            all_vulns = self.deduplicate_vulnerabilities(osv_vulns + nvd_vulns)
            
            # Add findings for each vulnerability
            for vuln in all_vulns:
                self.add_finding(SecurityFinding(
                    finding_id=f"DEP-{vuln.id}",
                    severity=vuln.severity,
                    title=f"Vulnerable Dependency: {name}",
                    description=vuln.description,
                    resource_id=f"{name}@{version}",
                    finding_type="dependency_vulnerability",
                    recommendation=f"Update to version {vuln.fixed_version}" if vuln.fixed_version else "Update to latest version",
                    details={
                        'package_name': name,
                        'current_version': version,
                        'fixed_version': vuln.fixed_version,
                        'references': vuln.references
                    }
                ))
                
        except Exception as e:
            logger.error(f"Error checking dependency {name}: {str(e)}")

    async def check_osv_database(self, package_name: str, version: str) -> List[DependencyVulnerability]:
        """Check OSV database for vulnerabilities"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "package": {
                        "name": package_name,
                        "ecosystem": "PyPI"
                    },
                    "version": version
                }
                
                async with session.post(self.osv_base_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        vulnerabilities = []
                        
                        for vuln in data.get('vulns', []):
                            vulnerabilities.append(DependencyVulnerability({
                                'id': vuln.get('id'),
                                'title': vuln.get('summary'),
                                'description': vuln.get('details'),
                                'severity': self._determine_severity(vuln),
                                'package_name': package_name,
                                'version': version,
                                'fixed_version': self._get_fixed_version(vuln),
                                'references': vuln.get('references', [])
                            }))
                            
                        return vulnerabilities
                    
            return []
            
        except Exception as e:
            logger.error(f"OSV database check failed: {str(e)}")
            return []

    @staticmethod
    def _determine_severity(vuln_data: Dict[str, Any]) -> str:
        """Determine vulnerability severity"""
        if 'severity' in vuln_data:
            sev = vuln_data['severity'][0].get('type', '').upper()
            if sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                return sev
        
        # Default to MEDIUM if no valid severity found
        return 'MEDIUM'

    @staticmethod
    def _get_fixed_version(vuln_data: Dict[str, Any]) -> Optional[str]:
        """Get fixed version from vulnerability data"""
        try:
            affected = vuln_data.get('affected', [])
            for item in affected:
                ranges = item.get('ranges', [])
                for range_info in ranges:
                    events = range_info.get('events', [])
                    for event in events:
                        if event.get('fixed'):
                            return event['fixed']
            return None
        except Exception:
            return None

    def deduplicate_vulnerabilities(self, vulns: List[DependencyVulnerability]) -> List[DependencyVulnerability]:
        """Deduplicate vulnerabilities based on ID"""
        seen_ids = set()
        unique_vulns = []
        
        for vuln in vulns:
            if vuln.id not in seen_ids:
                seen_ids.add(vuln.id)
                unique_vulns.append(vuln)
                
        return unique_vulns

    def get_scan_results(self) -> Dict[str, Any]:
        """Get formatted scan results"""
        findings = self.get_findings()
        
        return {
            'scan_id': self.scan_id,
            'scan_type': self.scan_type,
            'timestamp': datetime.utcnow().isoformat(),
            'findings': findings,
            'summary': {
                'total_dependencies': len(self.findings),
                'vulnerability_counts': {
                    'critical': sum(1 for f in findings if f['severity'] == 'CRITICAL'),
                    'high': sum(1 for f in findings if f['severity'] == 'HIGH'),
                    'medium': sum(1 for f in findings if f['severity'] == 'MEDIUM'),
                    'low': sum(1 for f in findings if f['severity'] == 'LOW')
                }
            }
        }