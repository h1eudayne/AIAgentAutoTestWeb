"""
Pytest configuration and fixtures for parallel test execution
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def worker_temp_dir(tmp_path_factory, worker_id):
    """
    Create worker-specific temporary directory for parallel test execution.
    Each worker gets its own isolated temp directory.
    """
    if worker_id == "master":
        # Not running with xdist or controller process
        temp_dir = tmp_path_factory.mktemp("test_data")
    else:
        # Worker process: gw0, gw1, gw2, etc.
        temp_dir = tmp_path_factory.mktemp(f"test_data_{worker_id}")
    
    yield temp_dir
    
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def isolated_temp_dir(worker_temp_dir):
    """
    Create isolated temporary directory for each test function.
    Ensures test isolation in parallel execution.
    """
    test_dir = worker_temp_dir / f"test_{id(object())}"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    yield test_dir
    
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def worker_id_fixture(worker_id):
    """
    Expose worker_id for tests that need to know which worker they're running on.
    Useful for debugging and worker-specific resource allocation.
    """
    return worker_id


def pytest_configure(config):
    """
    Configure pytest with custom markers and settings.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.
    """
    for item in items:
        # Add unit marker to all tests by default
        if "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)


def pytest_xdist_auto_num_workers(config):
    """
    Customize number of workers for parallel execution.
    Returns None to use default behavior (auto-detect CPUs).
    """
    import os
    
    # Check if running in CI environment
    if os.environ.get("CI"):
        # Use half of available CPUs in CI to avoid resource exhaustion
        import os
        return max(1, os.cpu_count() // 2)
    
    # Use default behavior (all CPUs)
    return None
