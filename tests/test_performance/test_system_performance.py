# tests/test_performance/test_system_performance.py

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

@pytest.mark.performance
class TestSystemPerformance:
    @pytest.fixture
    async def large_dataset(self):
        """Generate large test dataset."""
        return [
            {
                'package': f'test-package-{i}',
                'version': '1.0.0',
                'vulnerabilities': [
                    {
                        'severity': 'HIGH',
                        'description': f'Test vulnerability {j}',
                        'cve_id': f'CVE-2024-{i}{j}'
                    } for j in range(5)
                ]
            } for i in range(1000)
        ]

    @pytest.mark.asyncio
    async def test_scanner_performance(self, system_components, large_dataset):
        """Test scanner performance with large dataset."""
        scanner = system_components['scanner']
        
        start_time = time.time()
        findings = await scanner.execute_scan()
        execution_time = time.time() - start_time
        
        assert execution_time < 30  # Should complete within 30 seconds
        assert len(findings) > 0

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, system_components):
        """Test system performance under concurrent operations."""
        monitor = system_components['monitor']
        incident_manager = system_components['incident_manager']
        
        async def simulate_load():
            for _ in range(100):
                findings = await system_components['scanner'].execute_scan()
                await monitor._analyze_findings(findings)
                await asyncio.sleep(0.1)
        
        # Run multiple concurrent operations
        tasks = [simulate_load() for _ in range(5)]
        await asyncio.gather(*tasks)