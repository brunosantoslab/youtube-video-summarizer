"""
Pytest fixtures for integration tests
Author: Bruno Santos
"""
import pytest
from typing import Generator

# Import TestContainers fixtures from main conftest.py
# These are automatically available to tests in this directory
# No need to redefine them

@pytest.fixture
def integration_marker():
    """
    Marker fixture to identify integration tests.
    This fixture doesn't do anything but serves as a marker.
    """
    pass
