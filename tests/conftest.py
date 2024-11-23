import pytest
import asyncio
import os

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def mock_env():
    """Setup environment variables"""
    test_vars = {
        'AZURE_FUNCTION_NAME': 'test-function',
        'COSMOS_DB_CONNECTION': 'test_connection_string',
        'AZURE_STORAGE_CONNECTION': 'test_storage_connection'
    }
    os.environ.update(test_vars)
    yield