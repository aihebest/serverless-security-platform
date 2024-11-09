# tests/conftest.py

import pytest
import os
import sys
import asyncio
from typing import Dict, Any
from src.scanners.dependency_scanner import DependencyScanner
from src.monitors.security_monitor import SecurityMonitor
from src.incident_response.incident_manager import IncidentManager

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def dependency_scanner():
    """Fixture for dependency scanner with test configuration."""
    config = {
        'nvd_api_key': os.getenv('TEST_NVD_API_KEY', 'test-key'),
        'cache_duration': 3600,  # 1 hour for testing
        'test_mode': True
    }
    async with DependencyScanner(config) as scanner:
        yield scanner

@pytest.fixture
async def security_monitor():
    """Fixture for security monitor."""
    monitor = SecurityMonitor()
    await monitor.initialize()
    yield monitor
    await monitor.cleanup()

@pytest.fixture
async def incident_manager():
    """Fixture for incident manager."""
    manager = IncidentManager()
    await manager.initialize()
    yield manager
    await manager.cleanup()

@pytest.fixture
def sample_dependency_data() -> Dict[str, Any]:
    """Sample dependency data for testing."""
    return {
        "name": "test-project",
        "dependencies": [
            {"name": "requests", "version": "2.26.0"},
            {"name": "flask", "version": "2.0.1"},
            {"name": "sqlalchemy", "version": "1.4.23"}
        ]
    }

@pytest.fixture
def mock_nvd_response() -> Dict[str, Any]:
    """Mock NVD API response for testing."""
    return {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2021-test",
                    "description": [{"value": "Test vulnerability"}],
                    "metrics": {
                        "cvssMetricV31": [{
                            "cvssData": {
                                "baseScore": 7.5,
                                "severity": "HIGH"
                            }
                        }]
                    }
                }
            }
        ]
    }