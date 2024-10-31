import pytest
from src.monitors.threat_monitor import ThreatMonitor
from src.monitors.activity_monitor import ActivityMonitor

@pytest.mark.asyncio
class TestThreatMonitor:
    async def test_suspicious_activity_detection(self):
        monitor = ThreatMonitor()
        activity = {'content': 'DROP TABLE users;'}
        detected = await monitor.detect_suspicious_activity(activity)
        assert detected == True

@pytest.mark.asyncio
class TestActivityMonitor:
    async def test_audit_logging(self):
        monitor = ActivityMonitor()
        activity = {'type': 'security_event', 'details': 'test'}
        result = await monitor.audit_logging(activity)
        assert result['logged'] == True