"""Tests for the Cua bridge module."""

import pytest

from deskpilot.cua_bridge.actions import ActionResult, Actions, ScreenshotResult
from deskpilot.cua_bridge.agent import AgentResult, AgentStep, MockAgent
from deskpilot.cua_bridge.computer import (
    MockComputer,
    NativeComputer,
    ScreenInfo,
    get_computer,
)
from deskpilot.wizard.config import DeskPilotConfig


class TestMockComputer:
    """Tests for MockComputer."""

    @pytest.fixture
    def computer(self):
        """Create a MockComputer instance."""
        config = DeskPilotConfig()
        return MockComputer(config)

    @pytest.mark.asyncio
    async def test_connect_disconnect(self, computer):
        """Test connect and disconnect."""
        assert not computer.is_connected

        await computer.connect()
        assert computer.is_connected
        assert {"action": "connect"} in computer.actions

        await computer.disconnect()
        assert not computer.is_connected
        assert {"action": "disconnect"} in computer.actions

    @pytest.mark.asyncio
    async def test_screenshot(self, computer):
        """Test screenshot capture."""
        await computer.connect()

        image = await computer.screenshot()

        assert image is not None
        assert image.size == (1920, 1080)
        assert {"action": "screenshot"} in computer.actions

    @pytest.mark.asyncio
    async def test_click(self, computer):
        """Test click action."""
        await computer.connect()

        await computer.click(100, 200, button="left")

        assert {"action": "click", "x": 100, "y": 200, "button": "left"} in computer.actions

    @pytest.mark.asyncio
    async def test_double_click(self, computer):
        """Test double-click action."""
        await computer.connect()

        await computer.double_click(150, 250)

        assert {"action": "double_click", "x": 150, "y": 250} in computer.actions

    @pytest.mark.asyncio
    async def test_type_text(self, computer):
        """Test typing text."""
        await computer.connect()

        await computer.type_text("Hello, World!")

        assert {"action": "type_text", "text": "Hello, World!"} in computer.actions

    @pytest.mark.asyncio
    async def test_press_key(self, computer):
        """Test pressing a key."""
        await computer.connect()

        await computer.press_key("enter")

        assert {"action": "press_key", "key": "enter"} in computer.actions

    @pytest.mark.asyncio
    async def test_hotkey(self, computer):
        """Test hotkey combination."""
        await computer.connect()

        await computer.hotkey("ctrl", "c")

        assert {"action": "hotkey", "keys": ("ctrl", "c")} in computer.actions

    def test_screen_info(self, computer):
        """Test getting screen info."""
        info = computer.get_screen_info()

        assert isinstance(info, ScreenInfo)
        assert info.width == 1920
        assert info.height == 1080


class TestGetComputer:
    """Tests for get_computer factory function."""

    def test_get_mock_computer(self):
        """Test creating a mock computer."""
        computer = get_computer(mock=True)

        assert isinstance(computer, MockComputer)

    def test_get_native_computer_type(self):
        """Test that default mode returns NativeComputer type."""
        config = DeskPilotConfig()

        computer = get_computer(config, mock=False)

        assert isinstance(computer, NativeComputer)


class TestActions:
    """Tests for high-level Actions."""

    @pytest.fixture
    def actions(self):
        """Create Actions with MockComputer."""
        config = DeskPilotConfig()
        computer = MockComputer(config)
        return Actions(computer, config)

    @pytest.mark.asyncio
    async def test_screenshot_action(self, actions):
        """Test screenshot action."""
        await actions.computer.connect()

        result = await actions.screenshot()

        assert isinstance(result, ScreenshotResult)
        assert result.image is not None
        assert result.timestamp is not None

    @pytest.mark.asyncio
    async def test_click_with_coordinates(self, actions):
        """Test click with coordinates."""
        await actions.computer.connect()

        result = await actions.click(x=100, y=200)

        assert isinstance(result, ActionResult)
        assert result.success
        assert result.action == "click"
        assert result.details["x"] == 100
        assert result.details["y"] == 200

    @pytest.mark.asyncio
    async def test_click_without_coordinates_or_target(self, actions):
        """Test click fails without coordinates or target."""
        await actions.computer.connect()

        result = await actions.click()

        assert not result.success
        assert "must be specified" in result.error

    @pytest.mark.asyncio
    async def test_type_text_action(self, actions):
        """Test type_text action."""
        await actions.computer.connect()

        result = await actions.type_text("test input")

        assert result.success
        assert result.action == "type_text"
        assert result.details["length"] == 10

    @pytest.mark.asyncio
    async def test_launch_action(self, actions):
        """Test launch action."""
        await actions.computer.connect()

        result = await actions.launch("Calculator")

        assert result.success
        assert result.action == "launch"
        assert result.details["app"] == "Calculator"

    @pytest.mark.asyncio
    async def test_hotkey_action(self, actions):
        """Test hotkey action."""
        await actions.computer.connect()

        result = await actions.hotkey("ctrl", "c")

        assert result.success
        assert result.action == "hotkey"
        assert result.details["keys"] == ["ctrl", "c"]


class TestMockAgent:
    """Tests for MockAgent."""

    @pytest.fixture
    def agent(self):
        """Create a MockAgent instance."""
        config = DeskPilotConfig()
        computer = MockComputer(config)
        return MockAgent(computer, config)

    @pytest.mark.asyncio
    async def test_agent_run(self, agent):
        """Test agent run yields steps."""
        steps = []
        async for step in agent.run("test task", verbose=False):
            steps.append(step)

        assert len(steps) > 0
        assert all(isinstance(s, AgentStep) for s in steps)
        assert steps[0].step_number == 1

    @pytest.mark.asyncio
    async def test_agent_execute(self, agent):
        """Test agent execute returns result."""
        result = await agent.execute("test task", verbose=False)

        assert isinstance(result, AgentResult)
        assert result.success
        assert result.task == "test task"
        assert result.total_steps > 0
        assert result.final_answer is not None


class TestAgentStep:
    """Tests for AgentStep data class."""

    def test_agent_step_creation(self):
        """Test creating an AgentStep."""
        step = AgentStep(
            step_number=1,
            reasoning="I need to click the button",
            action="click",
            action_params={"x": 100, "y": 200},
        )

        assert step.step_number == 1
        assert step.reasoning == "I need to click the button"
        assert step.action == "click"
        assert step.action_params == {"x": 100, "y": 200}

    def test_agent_step_with_error(self):
        """Test AgentStep with error."""
        step = AgentStep(
            step_number=5,
            error="Connection lost",
        )

        assert step.error == "Connection lost"
        assert step.action is None


class TestAgentResult:
    """Tests for AgentResult data class."""

    def test_successful_result(self):
        """Test successful AgentResult."""
        steps = [
            AgentStep(step_number=1, action="screenshot"),
            AgentStep(step_number=2, action="click"),
        ]
        result = AgentResult(
            success=True,
            task="Open Calculator",
            steps=steps,
            final_answer="Calculator opened",
        )

        assert result.success
        assert result.total_steps == 2
        assert result.final_answer == "Calculator opened"

    def test_failed_result(self):
        """Test failed AgentResult."""
        result = AgentResult(
            success=False,
            task="Failed task",
            error="Could not connect",
        )

        assert not result.success
        assert result.error == "Could not connect"
        assert result.total_steps == 0
