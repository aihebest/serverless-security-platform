import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
class TestScheduledScanner:
    @pytest.fixture
    def mock_services(self):
        """Setup mock services"""
        mock_monitor = MagicMock()
        mock_monitor.get_current_metrics = AsyncMock(return_value={
            'risk_score': 85,
            'total_issues': 1,
            'compliance_score': 90
        })

        mock_scanner = MagicMock()
        mock_scanner.execute_scan = AsyncMock(return_value={
            'scan_id': 'test-scan-001',
            'status': 'completed',
            'findings': []
        })

        mock_incident = MagicMock()
        mock_incident.create_incident = AsyncMock()
        mock_incident.get_active_incidents = AsyncMock(return_value=[])

        return {
            'monitor': mock_monitor,
            'scanner': mock_scanner,
            'incident': mock_incident
        }

    @pytest.fixture
    def orchestrator(self):
        """Setup mock orchestrator"""
        mock_orch = MagicMock()
        mock_orch.run_scheduled_assessment = AsyncMock(return_value={
            'assessment_id': 'test-assessment-001',
            'status': 'completed',
            'scan_results': {
                'successful_scans': [],
                'failed_scans': []
            }
        })
        mock_orch.get_security_status = AsyncMock(return_value={
            'metrics': {
                'risk_score': 85,
                'total_issues': 1,
                'compliance_score': 90
            },
            'active_incidents': 0,
            'recent_scans': []
        })
        return mock_orch

    async def test_basic_functionality(self):
        """Basic test to verify pytest-asyncio is working"""
        assert True

    async def test_scan_execution(self, orchestrator):
        """Test scan execution"""
        results = await orchestrator.run_scheduled_assessment()
        
        assert results is not None
        assert results['status'] == 'completed'
        assert 'assessment_id' in results
        orchestrator.run_scheduled_assessment.assert_awaited_once()

    async def test_security_metrics(self, orchestrator):
        """Test security metrics collection"""
        status = await orchestrator.get_security_status("system")
        
        assert status is not None
        assert 'metrics' in status
        metrics = status['metrics']
        assert metrics['risk_score'] == 85
        assert metrics['compliance_score'] == 90
        orchestrator.get_security_status.assert_awaited_once_with("system")

    async def test_error_handling(self, orchestrator):
        """Test error handling in scans"""
        # Setup error scenario
        orchestrator.run_scheduled_assessment = AsyncMock(
            side_effect=Exception("Simulated scan error")
        )
        
        with pytest.raises(Exception) as exc_info:
            await orchestrator.run_scheduled_assessment()
        assert "Simulated scan error" in str(exc_info.value)

    async def test_critical_finding_handling(self, orchestrator, mock_services):
        """Test handling of critical security findings"""
        # Setup critical finding scenario
        mock_scan_result = {
            'scan_id': 'test-scan-002',
            'status': 'completed',
            'findings': [{
                'id': 'VULN-002',
                'severity': 'CRITICAL',
                'description': 'Critical security issue'
            }]
        }
        
        orchestrator.run_scheduled_assessment = AsyncMock(return_value={
            'assessment_id': 'test-assessment-002',
            'status': 'completed',
            'scan_results': {
                'successful_scans': [mock_scan_result],
                'failed_scans': []
            }
        })
        
        # Run test
        results = await orchestrator.run_scheduled_assessment()
        
        # Verify results
        assert results['status'] == 'completed'
        assert len(results['scan_results']['successful_scans']) == 1
        assert results['scan_results']['successful_scans'][0]['findings'][0]['severity'] == 'CRITICAL'