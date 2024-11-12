import pytest
from src.integration.security_manager import SecurityManager

@pytest.mark.asyncio
class TestSecurityManager:
    async def test_security_threat_blocking(self):
        config = {'test': True}
        manager = SecurityManager(config)
        threat_data = {'type': 'malicious', 'severity': 'high'}
        result = await manager.block_threat(threat_data)
        assert result['blocked'] is True
        assert result['reason'] == 'security_violation'