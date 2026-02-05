"""Cua SDK bridge for computer control."""

from deskpilot.cua_bridge.actions import ActionResult, Actions, ScreenshotResult, create_actions
from deskpilot.cua_bridge.agent import (
    AgentResult,
    AgentStep,
    DeskPilotAgent,
    MockAgent,
    create_agent,
)
from deskpilot.cua_bridge.computer import (
    BaseComputer,
    MockComputer,
    NativeComputer,
    WindowsComputer,
    get_computer,
)

__all__ = [
    # Computer classes
    "BaseComputer",
    "NativeComputer",
    "WindowsComputer",
    "MockComputer",
    "get_computer",
    # Actions
    "Actions",
    "ActionResult",
    "ScreenshotResult",
    "create_actions",
    # Agent
    "DeskPilotAgent",
    "MockAgent",
    "AgentStep",
    "AgentResult",
    "create_agent",
]
