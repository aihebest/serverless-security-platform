from unittest.mock import AsyncMock, MagicMock

class MockSecurityMonitor(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_current_metrics = AsyncMock(return_value={
            'risk_score': 85,
            'total_issues': 1,
            'compliance_score': 90
        })

class MockScanningService(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execute_scan = AsyncMock(return_value={
            'scan_id': 'test-scan-001',
            'status': 'completed',
            'findings': []
        })

class MockIncidentManager(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_incident = AsyncMock()
        self.get_active_incidents = AsyncMock(return_value=[])