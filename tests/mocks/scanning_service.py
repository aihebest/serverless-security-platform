"""Mock ScanningService implementation"""
from unittest.mock import AsyncMock, MagicMock

class MockScanningService(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execute_scan = AsyncMock(return_value={
            'scan_id': 'test-scan-001',
            'status': 'completed',
            'findings': []
        })
        self.get_recent_scans = AsyncMock(return_value=[])
        self.initialize = AsyncMock()