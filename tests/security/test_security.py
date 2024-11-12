# tests/security/test_security.py
import pytest
from src.core.orchestrator import SecurityOrchestrator
from datetime import datetime

@pytest.mark.asyncio
async def test_security_orchestrator(test_config):
    orchestrator = SecurityOrchestrator(test_config)
    assert orchestrator.config['environment'] == 'test'
    
    # Test security configuration
    security_config = await orchestrator.get_security_config()
    assert security_config is not None
    assert 'encryption' in security_config
    assert 'access_control' in security_config

@pytest.mark.asyncio
async def test_security_metrics():
    orchestrator = SecurityOrchestrator()
    metrics = await orchestrator.collect_security_metrics()
    
    assert metrics is not None
    assert 'timestamp' in metrics
    assert 'risk_score' in metrics
    assert 'active_threats' in metrics
    assert isinstance(metrics['timestamp'], datetime)

@pytest.mark.asyncio
async def test_security_incident_creation():
    orchestrator = SecurityOrchestrator()
    incident_data = {
        'severity': 'HIGH',
        'type': 'VULNERABILITY',
        'description': 'Critical dependency vulnerability detected'
    }
    
    incident = await orchestrator.create_security_incident(incident_data)
    assert incident['id'] is not None
    assert incident['status'] == 'OPEN'
    assert incident['severity'] == 'HIGH'