# tests/test_scanners/test_base_scanner.py

import pytest
import asyncio
from datetime import datetime
from src.scanners.base_scanner import BaseScanner, ScanResult

class MockScanner(BaseScanner):
    def __init__(self, config, should_fail=False):
        super().__init__(config)
        self.should_fail = should_fail
        self.pre_scan_called = False
        self.post_scan_called = False

    async def scan(self):
        if self.should_fail:
            raise ValueError("Scan failed")
        return [
            ScanResult(
                scan_id="test-1",
                timestamp=datetime.utcnow(),
                severity="HIGH",
                finding_type="TEST",
                description="Test finding",
                affected_resource="test-resource",
                recommendation="Test recommendation"
            )
        ]

    async def validate_configuration(self):
        return not self.should_fail

    async def pre_scan_hooks(self):
        await super().pre_scan_hooks()
        self.pre_scan_called = True

    async def post_scan_hooks(self, results):
        await super().post_scan_hooks(results)
        self.post_scan_called = True

@pytest.mark.asyncio
async def test_successful_scan(test_config):
    scanner = MockScanner(test_config)
    results = await scanner.execute_scan()
    
    assert len(results) == 1
    assert results[0].severity == "HIGH"
    assert scanner.pre_scan_called
    assert scanner.post_scan_called

@pytest.mark.asyncio
async def test_failed_scan(test_config):
    scanner = MockScanner(test_config, should_fail=True)
    
    with pytest.raises(ValueError):
        await scanner.execute_scan()

@pytest.mark.asyncio
async def test_scan_result_serialization():
    result = ScanResult(
        scan_id="test-1",
        timestamp=datetime.utcnow(),
        severity="HIGH",
        finding_type="TEST",
        description="Test finding",
        affected_resource="test-resource",
        recommendation="Test recommendation",
        metadata={"key": "value"}
    )
    
    serialized = result.to_dict()
    assert serialized["scan_id"] == "test-1"
    assert serialized["severity"] == "HIGH"
    assert "metadata" in serialized