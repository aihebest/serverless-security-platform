# tests/test_integration/test_security_scanning.py

import pytest
import asyncio
from datetime import datetime, timedelta
from src.scanners.dependency_scanner import DependencyScanner
from src.monitors.security_monitor import SecurityMonitor
from src.storage.findings_storage import FindingsStorage

@pytest.mark.integration
class TestSecurityScanningIntegration:
    @pytest.fixture
    async def setup_components(self, mock_config):
        # Initialize components
        scanner = DependencyScanner(mock_config)
        monitor = SecurityMonitor(mock_config)
        storage = FindingsStorage(mock_config)
        
        monitor.register_scanner(scanner)
        
        return scanner, monitor, storage

    @pytest.mark.asyncio
    async def test_full_scanning_cycle(self, setup_components):
        scanner, monitor, storage = setup_components
        
        # Run scan and collect findings
        findings = await scanner.execute_scan()
        assert len(findings) > 0
        
        # Store findings
        for finding in findings:
            await storage.store_finding(finding)
        
        # Verify storage
        stored_findings = await storage.get_findings(
            start_time=datetime.utcnow() - timedelta(hours=1)
        )
        assert len(stored_findings) == len(findings)
        
        # Verify monitoring alerts
        await monitor._analyze_findings(findings)
        # Add assertions for alerts based on your alert configuration

    @pytest.mark.asyncio
    async def test_report_generation(self, setup_components):
        scanner, monitor, storage = setup_components
        
        # Run scan
        findings = await scanner.execute_scan()
        
        # Generate report
        report = await self._generate_security_report(findings)
        
        assert report['scan_summary']['total_findings'] == len(findings)
        assert 'severity_breakdown' in report
        assert 'recommendations' in report

    async def _generate_security_report(self, findings):
        severity_counts = {}
        for finding in findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            
        return {
            'scan_summary': {
                'total_findings': len(findings),
                'scan_time': datetime.utcnow().isoformat(),
                'severity_breakdown': severity_counts
            },
            'recommendations': [
                {
                    'severity': finding.severity,
                    'resource': finding.resource,
                    'recommendation': finding.recommendation
                }
                for finding in findings
            ]
        }