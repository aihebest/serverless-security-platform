# tests/security/test_monitoring.py
import pytest
from src.monitors.security_monitor import SecurityMonitor
from src.monitors.alert_manager import AlertManager

@pytest.mark.asyncio
async def test_security_monitor_initialization(test_config):
    monitor = SecurityMonitor(test_config)
    assert monitor is not None
    assert monitor.config['resource_group'] == test_config['resource_group']

@pytest.mark.asyncio
async def test_alert_generation():
    alert_manager = AlertManager()
    alert_data = {
        'type': 'SecurityViolation',
        'severity': 'High',
        'resource': 'test-resource',
        'description': 'Unauthorized access attempt detected'
    }
    
    alert = await alert_manager.create_alert(alert_data)
    assert alert['id'] is not None
    assert alert['status'] == 'Active'
    assert alert['severity'] == 'High'

@pytest.mark.asyncio
async def test_metric_collection():
    monitor = SecurityMonitor()
    metrics = await monitor.collect_metrics()
    
    assert metrics is not None
    assert 'resource_metrics' in metrics
    assert 'security_events' in metrics
    assert 'performance_metrics' in metrics