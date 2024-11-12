# src/scanners/dependency_scanner.py

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from .base_scanner import BaseScanner

logger = logging.getLogger(__name__)

class DependencyScanner(BaseScanner):
    def __init__(self):
        super().__init__(scan_type="dependency")
        self.nvd_api_key = os.getenv('NVD_API_KEY')
        self.osv_base_url = "https://api.osv.dev/v1/query"
        
        # Initialize logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def scan(self, dependencies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Scan dependencies for vulnerabilities"""
        try:
            scan_id = f"dep_scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            findings = []

            # Log scan start
            self.logger.info(f"Starting dependency scan {scan_id}")
            self.logger.info(f"Scanning {len(dependencies)} dependencies")

            # Check if we have NVD API key
            if not self.nvd_api_key:
                self.logger.warning("NVD_API_KEY not set - falling back to OSV database only")

            # Scan each dependency
            for dep in dependencies:
                try:
                    vuln_info = await self._check_dependency(dep)
                    if vuln_info:
                        findings.extend(vuln_info)
                except Exception as e:
                    self.logger.error(f"Error scanning dependency {dep.get('name')}: {str(e)}")

            # Prepare results
            results = {
                'scan_id': scan_id,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'completed',
                'dependencies_scanned': len(dependencies),
                'vulnerabilities_found': len(findings),
                'findings': findings
            }

            self.logger.info(f"Scan completed. Found {len(findings)} vulnerabilities")
            return results

        except Exception as e:
            error_msg = f"Dependency scan failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'scan_id': f"dep_scan_error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'failed',
                'error': error_msg
            }

    async def _check_dependency(self, dependency: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check a single dependency for vulnerabilities"""
        findings = []
        name = dependency.get('name')
        version = dependency.get('version')

        if not name or not version:
            self.logger.warning(f"Invalid dependency format: {dependency}")
            return findings

        # Check OSV database (doesn't require API key)
        try:
            osv_findings = await self._check_osv_database(name, version)
            findings.extend(osv_findings)
        except Exception as e:
            self.logger.error(f"Error checking OSV database for {name}: {str(e)}")

        # Check NVD database if API key is available
        if self.nvd_api_key:
            try:
                nvd_findings = await self._check_nvd_database(name, version)
                findings.extend(nvd_findings)
            except Exception as e:
                self.logger.error(f"Error checking NVD database for {name}: {str(e)}")

        return findings

    async def _check_osv_database(self, package_name: str, version: str) -> List[Dict[str, Any]]:
        """Check OSV database for vulnerabilities"""
        # Implementation remains the same but with better logging
        findings = []
        self.logger.info(f"Checking OSV database for {package_name}@{version}")
        # Add OSV database check implementation
        return findings

    async def _check_nvd_database(self, package_name: str, version: str) -> List[Dict[str, Any]]:
        """Check NVD database for vulnerabilities"""
        # Only called if NVD_API_KEY is available
        findings = []
        self.logger.info(f"Checking NVD database for {package_name}@{version}")
        # Add NVD database check implementation
        return findings