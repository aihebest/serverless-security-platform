from unittest.mock import AsyncMock

class MockSecurityMonitor:
    """Mock implementation of SecurityMonitor"""
    def __init__(self):
        self.get_current_metrics = AsyncMock(return_value={
            'risk_score': 85,
            'total_issues': 1,
            'compliance_score': 90
        })
        self.process_scan_results = AsyncMock(return_value=True)
        self.initialize = AsyncMock()