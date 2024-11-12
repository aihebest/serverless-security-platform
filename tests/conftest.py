# tests/conftest.py
import pytest
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Fixture for test configuration
@pytest.fixture
def test_config():
    return {
        "environment": "test",
        "resource_group": "Production",
        "location": "westeurope"
    }

# Fixture for mock Azure credentials
@pytest.fixture
def mock_credentials():
    return {
        "clientId": "test-client-id",
        "clientSecret": "test-client-secret",
        "subscriptionId": "test-subscription-id",
        "tenantId": "test-tenant-id"
    }