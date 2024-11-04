# tests/conftest.py

import pytest
import asyncio
from typing import Dict, Any
import json
import os

@pytest.fixture
def test_config() -> Dict[str, Any]:
    return {
        'scan_interval': 300,
        'severity_threshold': 'HIGH',
        'notification_endpoints': ['http://localhost:7071/api/notify']
    }

@pytest.fixture
def mock_scan_result():
    return {
        'scan_id': 'test-scan-001',
        'timestamp': '2024-01-01T00:00:00Z',
        'severity': 'HIGH',
        'finding_type': 'DEPENDENCY_VULNERABILITY',
        'description': 'Critical vulnerability found',
        'affected_resource': 'package@1.0.0',
        'recommendation': 'Update to latest version'
    }

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()