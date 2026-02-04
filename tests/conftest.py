"""Pytest configuration and shared fixtures."""

import pytest

from deskpilot.cua_bridge.computer import MockComputer
from deskpilot.wizard.config import DeskPilotConfig


@pytest.fixture
def config():
    """Create a default DeskPilotConfig."""
    return DeskPilotConfig()


@pytest.fixture
def mock_computer(config):
    """Create a connected MockComputer."""
    computer = MockComputer(config)
    return computer


@pytest.fixture
async def connected_mock_computer(mock_computer):
    """Create a connected MockComputer (async fixture)."""
    await mock_computer.connect()
    yield mock_computer
    await mock_computer.disconnect()
