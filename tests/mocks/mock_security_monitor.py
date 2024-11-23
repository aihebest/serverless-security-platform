"""Mock SecurityMonitor implementation"""
from unittest.mock import AsyncMock, MagicMock

class MockSecurityMonitor(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_current_metrics = AsyncMock(return_value={
            'risk_score': 85,
            'total_issues': 1,
            'compliance_score': 90
        })
        self.process_scan_results = AsyncMock(return_value=True)
        self.initialize = AsyncMock()