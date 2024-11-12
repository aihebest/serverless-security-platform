# tests/security/test_scanners.py
import pytest
from src.scanners.dependency_scanner import DependencyScanner
from src.scanners.scanning_service import ScanningService

@pytest.mark.asyncio
async def test_scanner_initialization(test_config):
    scanner = DependencyScanner()
    assert scanner is not None
    assert scanner.config['environment'] == test_config['environment']

@pytest.mark.asyncio
async def test_dependency_scan():
    scanner = DependencyScanner()
    test_dependencies = [
        {"name": "requests", "version": "2.26.0"},
        {"name": "django", "version": "2.2.24"}
    ]
    
    scan_result = await scanner.scan_dependencies(test_dependencies)
    assert scan_result is not None
    assert "vulnerabilities" in scan_result
    assert "scan_id" in scan_result
    assert "timestamp" in scan_result

@pytest.mark.asyncio
async def test_scanning_service():
    service = ScanningService()
    scan_config = {
        "scan_type": "dependency",
        "project_id": "test-project",
        "dependencies": [
            {"name": "requests", "version": "2.26.0"}
        ]
    }
    
    result = await service.run_scan(scan_config)
    assert result['status'] == 'completed'
    assert result['project_id'] == scan_config['project_id']