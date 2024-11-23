"""Mock IncidentManager implementation"""
from unittest.mock import AsyncMock, MagicMock

class MockIncidentManager(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_incident = AsyncMock(return_value={'incident_id': 'test-001'})
        self.get_active_incidents = AsyncMock(return_value=[])
        self.process_scan_findings = AsyncMock(return_value=True)
        self.initialize = AsyncMock()