"""
Pytest configuration and fixtures for qufe tests
"""
import pytest
import sys
import os

# Add the src directory to the Python path for testing
# This ensures we can import qufe modules during testing
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture(scope="session")
def qufe_module():
    """Fixture to ensure qufe module is available for all tests"""
    try:
        import qufe
        return qufe
    except ImportError as e:
        pytest.skip(f"qufe module not available: {e}")


@pytest.fixture
def temp_directory():
    """Fixture that provides a temporary directory for file operations"""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_data():
    """Fixture that provides sample data for testing"""
    return {
        'simple_list': [1, 2, 3, 4, 5],
        'nested_list': [[1, 2], [3, [4, 5]], 6],
        'simple_dict': {'key1': 'value1', 'key2': 'value2'},
        'nested_dict': {
            'level1': {
                'level2': {
                    'level3': 'deep_value'
                }
            }
        },
        'text_with_brackets': 'Hello (world) test [example] end {final}',
        'mixed_data': {
            'numbers': [1, 2, 3],
            'strings': ['a', 'b', 'c'],
            'nested': {'inner': [4, 5, 6]}
        }
    }


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_db: marks tests that require database connection"
    )
    config.addinivalue_line(
        "markers", "requires_browser: marks tests that require browser setup"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle optional dependencies"""
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    skip_integration = pytest.mark.skip(reason="integration tests skipped by default")
    
    for item in items:
        if "slow" in item.keywords:
            if not config.getoption("--runslow", default=False):
                item.add_marker(skip_slow)
        if "integration" in item.keywords:
            if not config.getoption("--runintegration", default=False):
                item.add_marker(skip_integration)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--runslow", 
        action="store_true", 
        default=False, 
        help="run slow tests"
    )
    parser.addoption(
        "--runintegration",
        action="store_true",
        default=False,
        help="run integration tests"
    )