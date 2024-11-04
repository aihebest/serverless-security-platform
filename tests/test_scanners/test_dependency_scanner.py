# tests/test_scanners/test_dependency_scanner.py

import pytest
import aiohttp
from unittest.mock import Mock, patch
from src.scanners.dependency_scanner import DependencyScanner

@pytest.fixture
def mock_vulnerability_response():
    return [
        {
            "severity": "HIGH",
            "description": "Security vulnerability in package",
            "recommendation": "Update to version 2.0.0",
            "cve_id": "CVE-2024-1234"
        }
    ]

@pytest.fixture
def dependency_scanner_config():
    return {
        "vulnerability_database_url": "http://test-vuln-db.com",
        "scan_depth": "DEEP"
    }

@pytest.mark.asyncio
async def test_dependency_scanner_initialization(dependency_scanner_config):
    scanner = DependencyScanner(dependency_scanner_config)
    assert scanner.vuln_db_url == "http://test-vuln-db.com"
    assert scanner.scan_depth == "DEEP"

@pytest.mark.asyncio
async def test_dependency_scanner_validation(dependency_scanner_config):
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        scanner = DependencyScanner(dependency_scanner_config)
        is_valid = await scanner.validate_configuration()
        assert is_valid

@pytest.mark.asyncio
async def test_package_scanning(dependency_scanner_config, mock_vulnerability_response):
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = Mock(
            return_value=mock_vulnerability_response
        )
        
        scanner = DependencyScanner(dependency_scanner_config)
        results = await scanner.scan_package({
            "name": "test-package",
            "version": "1.0.0"
        })
        
        assert len(results) == 1
        assert results[0].severity == "HIGH"
        assert results[0].metadata["cve_id"] == "CVE-2024-1234"