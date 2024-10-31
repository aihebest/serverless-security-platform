# tests/security/test_scanners.py
import pytest
from src.scanners.dependency_scanner import DependencyScanner
from src.scanners.config_scanner import ConfigurationScanner

@pytest.mark.asyncio
class TestDependencyScanner:
    async def test_vulnerability_check(self):
        scanner = DependencyScanner()
        test_dependency = {
            'name': 'requests',
            'version': '2.0.0'
        }
        result = await scanner.check_vulnerability(test_dependency)
        assert result['has_vulnerabilities'] == True

    async def test_scan_dependencies(self):
        scanner = DependencyScanner()
        result = await scanner.scan_dependencies('requirements.txt')
        assert 'scan_time' in result
        assert 'status' in result
        assert result['status'] == 'completed'

@pytest.mark.asyncio
class TestConfigurationScanner:
    async def test_scan_config(self):
        scanner = ConfigurationScanner()
        test_config = {
            'azure_function_name': 'test-function',
            'resource_group': 'test-rg'
        }
        result = await scanner.scan_config(test_config)
        assert 'timestamp' in result
        assert 'scan_status' in result