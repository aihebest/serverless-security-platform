# tests/test_scanners/test_dependency_scanner.py

import pytest
import aiohttp
from unittest.mock import MagicMock, patch
from src.scanners.dependency_scanner import DependencyScanner

@pytest.mark.asyncio
async def test_dependency_scanner_initialization(mock_config):
    scanner = DependencyScanner(mock_config)
    assert scanner.vuln_db_url == mock_config["vulnerability_database_url"]
    assert scanner.severity_threshold == "LOW"

@pytest.mark.asyncio
async def test_dependency_scanner_scan(mock_config, mock_requirements_file, mock_vulnerability_data):
    scanner = DependencyScanner(mock_config)
    scanner.requirements_paths = [mock_requirements_file]

    # Mock the vulnerability database response
    async def mock_get(*args, **kwargs):
        response = MagicMock()
        response.status = 200
        response.json = MagicMock(return_value=[mock_vulnerability_data["requests"][0]])
        return response

    with patch("aiohttp.ClientSession.get", side_effect=mock_get):
        findings = await scanner.scan()
        
        assert len(findings) > 0
        assert findings[0].severity == "HIGH"
        assert "CVE-2023-1234" in findings[0].metadata["cve_id"]

@pytest.mark.asyncio
async def test_dependency_scanner_validation(mock_config, mock_requirements_file):
    scanner = DependencyScanner(mock_config)
    scanner.requirements_paths = [mock_requirements_file]
    
    is_valid = await scanner.validate_configuration()
    assert is_valid

@pytest.mark.asyncio
async def test_dependency_scanner_invalid_config(mock_config):
    invalid_config = mock_config.copy()
    invalid_config["vulnerability_database_url"] = ""
    
    scanner = DependencyScanner(invalid_config)
    is_valid = await scanner.validate_configuration()
    assert not is_valid