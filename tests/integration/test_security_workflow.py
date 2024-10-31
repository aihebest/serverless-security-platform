# tests/integration/test_security_workflow.py
import pytest
from src.integration import SecurityWorkflow

@pytest.mark.asyncio
class TestSecurityWorkflow:
    async def test_incident_response(self):
        config = {'test_config': True}
        workflow = SecurityWorkflow(config)
        
        result = await workflow.handle_security_incident({
            'type': 'security_threat',
            'severity': 'high'
        })
        
        assert result['incident_handled']
        assert isinstance(result['mitigation_steps'], list)