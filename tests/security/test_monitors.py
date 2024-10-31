import pytest
from src.monitors.request_analyzer import RequestAnalyzer

@pytest.mark.asyncio
class TestRequestAnalyzer:
    async def test_malicious_pattern_detection(self):
        analyzer = RequestAnalyzer()
        request_data = {
            'body': 'DROP TABLE users;',
            'headers': {'content-type': 'application/json'}
        }
        result = await analyzer.analyze_request(request_data)
        assert result['threats_detected'] == True