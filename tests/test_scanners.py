import pytest
from src.scanners.dependency_scanner import DependencyScanner
from src.scanners.config_scanner import ConfigurationScanner

@pytest.mark.asyncio
class TestDependencyScanner:
    async def test_vulnerability_check(self):
        scanner = DependencyScanner()
        dependency = {'name': 'requests', 'version': '2.0.0'}
        result = await scanner.check_vulnerability(dependency)
        assert result['has_vulnerabilities'] == True

    async def test_parse_requirements(self):
        scanner = DependencyScanner()
        requirements = scanner.parse_requirements('requirements.txt')
        assert isinstance(requirements, list)

@pytest.mark.asyncio
class TestConfigScanner:
    async def test_authentication_check(self):
        scanner = ConfigurationScanner()
        result = await scanner.test_authentication()
        assert result['authenticated'] == True