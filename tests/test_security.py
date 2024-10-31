import pytest
from src.scanners.dependency_scanner import DependencyScanner
from src.monitors.request_analyzer import RequestAnalyzer

@pytest.mark.asyncio
async def test_dependency_scanner():
    scanner = DependencyScanner()
    result = await scanner.scan_dependencies('requirements.txt')
    assert 'scan_time' in result
    assert 'vulnerabilities_found' in result
    
@pytest.mark.asyncio
async def test_request_analyzer():
    analyzer = RequestAnalyzer()
    request_data = {
        'ip_address': '192.168.1.1',
        'request_id': 'test-123',
        'method': 'POST',
        'path': '/api/data',
        'headers': {'content-type': 'application/json'},
        'body': '{"data": "test"}'
    }
    
    result = await analyzer.analyze_request(request_data)
    assert 'threats_detected' in result
    assert 'timestamp' in result