"""Test configuration"""

TEST_CONFIG = {
    'test_project_id': 'test-project',
    'timeout': 30,
    'retry_attempts': 3
}

MOCK_RESPONSES = {
    'security_metrics': {
        'risk_score': 85,
        'total_issues': 1,
        'compliance_score': 90
    },
    'scan_result': {
        'scan_id': 'test-scan-001',
        'status': 'completed',
        'findings': []
    }
}