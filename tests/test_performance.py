import pytest
from datetime import datetime
import asyncio
from unittest.mock import AsyncMock, patch

@pytest.mark.performance
class TestPerformance:
    @pytest.fixture
    async def orchestrator(self):
        """Setup test orchestrator"""
        with patch('src.core.orchestrator.SecurityOrchestrator') as mock_orch:
            instance = mock_orch.return_value
            instance.scanning_service.execute_scan = AsyncMock(return_value={
                'scan_id': 'test-scan-001',
                'status': 'completed',
                'findings': []
            })
            yield instance

    async def test_scan_execution_time(self, orchestrator):
        """Test that individual scans complete within acceptable time"""
        start_time = datetime.now()
        
        await orchestrator.run_scheduled_assessment()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        assert execution_time < 5.0, f"Scan took too long: {execution_time} seconds"

    async def test_concurrent_scans(self, orchestrator):
        """Test handling of multiple concurrent scans"""
        start_time = datetime.now()
        
        # Execute multiple scans concurrently
        scan_tasks = [
            orchestrator.run_scheduled_assessment()
            for _ in range(5)
        ]
        results = await asyncio.gather(*scan_tasks)
        
        # Verify execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        assert execution_time < 10.0, f"Concurrent scans took too long: {execution_time} seconds"
        
        # Verify results
        assert len(results) == 5, "Not all scans completed"
        assert all(r['status'] == 'completed' for r in results)

    async def test_resource_usage(self, orchestrator):
        """Test resource utilization during scanning"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Execute scan
        await orchestrator.run_scheduled_assessment()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 100, f"Memory usage increased by {memory_increase}MB"

    async def test_database_performance(self, orchestrator):
        """Test database operation performance"""
        start_time = datetime.now()
        
        # Execute scan and store results
        scan_result = await orchestrator.run_scheduled_assessment()
        
        # Verify storage time
        storage_time = (datetime.now() - start_time).total_seconds()
        assert storage_time < 2.0, f"Database operation took too long: {storage_time} seconds"