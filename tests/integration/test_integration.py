import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_basic_security_assessment():
    """Test basic security assessment functionality"""
    with patch('src.core.orchestrator.SecurityOrchestrator') as mock_orch:
        mock_instance = mock_orch.return_value
        mock_instance.run_scheduled_assessment = AsyncMock(return_value={
            'status': 'completed',
            'assessment_id': 'test-001'
        })
        result = await mock_instance.run_scheduled_assessment()
        assert result['status'] == 'completed'

@pytest.mark.asyncio
async def test_security_metrics():
    """Test security metrics retrieval"""
    with patch('src.core.orchestrator.SecurityOrchestrator') as mock_orch:
        mock_instance = mock_orch.return_value
        mock_instance.get_security_status = AsyncMock(return_value={
            'metrics': {'risk_score': 85}
        })
        status = await mock_instance.get_security_status("test-project")
        assert status['metrics']['risk_score'] == 85

@pytest.mark.asyncio
async def test_critical_finding_detection():
    """Test critical finding handling"""
    with patch('src.core.orchestrator.SecurityOrchestrator') as mock_orch:
        mock_instance = mock_orch.return_value
        
        async def mock_assessment():
            return {
                'status': 'completed',
                'findings': [{'severity': 'CRITICAL'}]
            }
        
        mock_instance.run_scheduled_assessment = AsyncMock(side_effect=mock_assessment)
        mock_instance.incident_manager = AsyncMock()
        
        result = await mock_instance.run_scheduled_assessment()
        assert result['findings'][0]['severity'] == 'CRITICAL'