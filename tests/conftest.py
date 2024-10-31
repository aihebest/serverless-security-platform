import pytest
import os
from datetime import datetime

@pytest.fixture
def test_config():
    """Provide test configuration"""
    return {
        'environment': 'test',
        'azure_function_name': 'test-function',
        'subscription_id': 'test-subscription',
        'resource_group': 'test-rg'
    }

@pytest.fixture
def sample_security_event():
    """Provide sample security event data"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'severity': 'high',
        'source': 'test-scanner',
        'description': 'Potential security violation detected',
        'affected_resource': 'test-function'
    }

@pytest.fixture
def mock_azure_context(mocker):
    """Mock Azure Functions context"""
    context = mocker.MagicMock()
    context.function_name = "test_function"
    context.invocation_id = "test_invocation_id"
    return context