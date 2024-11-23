# 1. First, create a new file: src/scanners/scheduled_scanner.py

from datetime import datetime
import asyncio
from typing import Dict, List

class ScheduledScanManager:
    def __init__(self):
        self.scanners = {
            'vulnerability': VulnerabilityScanner(),
            'sast': SASTScanner(),
            'container': ContainerScanner(),
            'compliance': ComplianceScanner()
        }
        
    async def run_scheduled_scan(self, scan_type: str) -> Dict:
        """
        Execute a scheduled scan of the specified type
        """
        try:
            scanner = self.scanners.get(scan_type)
            if not scanner:
                raise ValueError(f"Invalid scanner type: {scan_type}")
            
            # Start scan
            scan_start = datetime.utcnow()
            results = await scanner.scan()
            scan_duration = (datetime.utcnow() - scan_start).total_seconds()
            
            # Process results
            processed_results = await self._process_results(results, scan_type, scan_duration)
            return processed_results
            
        except Exception as e:
            await self._handle_scan_error(scan_type, str(e))
            raise
            
    async def _process_results(self, results: List, scan_type: str, duration: float) -> Dict:
        """
        Process and store scan results
        """
        processed_results = {
            'scan_type': scan_type,
            'timestamp': datetime.utcnow().isoformat(),
            'duration': duration,
            'findings': results,
            'summary': self._generate_summary(results)
        }
        
        # Store results in Cosmos DB
        await self._store_results(processed_results)
        
        # Check if alerts needed
        await self._check_alerts(processed_results)
        
        return processed_results
        
    def _generate_summary(self, results: List) -> Dict:
        """
        Generate summary of scan results
        """
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in results:
            severity_counts[finding.severity] += 1
            
        return {
            'total_findings': len(results),
            'severity_breakdown': severity_counts
        }
