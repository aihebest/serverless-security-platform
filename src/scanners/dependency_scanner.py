# src/scanners/dependency_scanner.py

import asyncio
import subprocess
import sys
import os
from typing import Dict, List, Any, Optional
import json
import pkg_resources
import requests
from datetime import datetime, timedelta
from functools import lru_cache
import logging
from ratelimit import limits, sleep_and_retry
import aiohttp
import async_timeout
from src.monitoring.app_insights import app_insights

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyScanner:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.nvd_api_key = self.config.get('nvd_api_key')
        self.cache_dir = os.path.join(os.path.dirname(__file__), '.cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    async def scan(self, requirements_file: str = 'requirements.txt') -> Dict[str, Any]:
        """Scan Python dependencies for security vulnerabilities."""
        try:
            # Track scan start
            app_insights.track_event("ScanStarted", {
                "requirements_file": requirements_file
            })
            
            start_time = datetime.utcnow()
            
            # Get installed packages
            packages = self._get_installed_packages(requirements_file)
            
            # Track packages found
            app_insights.track_metric("PackagesScanned", len(packages))
            
            # Scan for vulnerabilities
            vulnerabilities = await self._check_vulnerabilities(packages)
            
            # Generate report
            report = self._generate_report(packages, vulnerabilities)
            
            # Track scan completion
            scan_duration = (datetime.utcnow() - start_time).total_seconds()
            app_insights.track_metric("ScanDuration", scan_duration)
            app_insights.track_event("ScanCompleted", {
                "vulnerabilities_found": len(vulnerabilities),
                "scan_duration": scan_duration
            })
            
            return {
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat(),
                'scan_type': 'dependency',
                'findings': report['findings'],
                'summary': report['summary']
            }
        
        except Exception as e:
            # Track scan failure
            app_insights.track_exception(e)
            return {
                'status': 'failed',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }