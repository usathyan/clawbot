"""Tests for WinAppDriver integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from deskpilot.cua_bridge.winappdriver import (
    LEGACY_ELEMENT_KEY,
    W3C_ELEMENT_KEY,
    WinAppDriverClient,
    WinElement,
)
from deskpilot.wizard.config import DeskPilotConfig, WinAppDriverConfig, WindowsConfig


class TestWinAppDriverConfig:
    """Tests for WinAppDriver configuration models."""

    def test_default_config(self):
        """Test default WinAppDriver config values."""
        config = WinAppDriverConfig()

        assert config.enabled is True
        assert config.port == 4723
        assert config.auto_start is True
        assert config.timeout == 10.0
        assert "WinAppDriver.exe" in config.path

    def test_windows_config(self):
        """Test WindowsConfig with WinAppDriver settings."""
        config = WindowsConfig()

        assert config.winappdriver.enabled is True
        assert config.fallback_on_failure is True
        assert config.click_pause == 0.1
        assert config.typing_interval == 0.05

    def test_disabled_winappdriver(self):
        """Test disabling WinAppDriver."""
        config = WindowsConfig(
            winappdriver=WinAppDriverConfig(enabled=False)
        )

        assert config.winappdriver.enabled is False

    def test_deskpilot_config_has_windows(self):
        """Test that DeskPilotConfig includes Windows section."""
        config = DeskPilotConfig()

        assert hasattr(config, "windows")
        assert isinstance(config.windows, WindowsConfig)
        assert config.windows.winappdriver.port == 4723


class TestWinElement:
    """Tests for WinElement."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock WinAppDriverClient."""
        session = MagicMock(spec=WinAppDriverClient)
        session._post = AsyncMock(return_value={})
        session._get = AsyncMock(return_value={"value": "test"})
        return session

    @pytest.mark.asyncio
    async def test_click(self, mock_session):
        """Test element click."""
        element = WinElement(session=mock_session, element_id="elem-123")

        await element.click()

        mock_session._post.assert_called_once_with("element/elem-123/click")

    @pytest.mark.asyncio
    async def test_double_click(self, mock_session):
        """Test element double-click uses Actions API."""
        element = WinElement(session=mock_session, element_id="elem-456")

        await element.double_click()

        mock_session._post.assert_called_once()
        call_args = mock_session._post.call_args
        assert call_args[0][0] == "actions"
        actions_json = call_args[1]["json"]
        assert "actions" in actions_json

    @pytest.mark.asyncio
    async def test_get_attribute(self, mock_session):
        """Test getting element attribute."""
        element = WinElement(session=mock_session, element_id="elem-789")

        result = await element.get_attribute("Name")

        mock_session._get.assert_called_once_with(
            "element/elem-789/attribute/Name"
        )
        assert result == "test"


class TestWinAppDriverClient:
    """Tests for WinAppDriverClient."""

    def test_init(self):
        """Test client initialization."""
        client = WinAppDriverClient(port=4724, timeout=5.0)

        assert client.base_url == "http://127.0.0.1:4724"
        assert client.timeout == 5.0
        assert client.session_id is None

    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test session creation with mocked HTTP."""
        client = WinAppDriverClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "value": {"sessionId": "test-session-id"}
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_http

            await client.create_session()

            assert client.session_id == "test-session-id"
            mock_http.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_element_from_point_found(self):
        """Test finding element at coordinates."""
        client = WinAppDriverClient()
        client.session_id = "test-session"
        client._client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": {LEGACY_ELEMENT_KEY: "found-element-id"}
        }
        client._client.post = AsyncMock(return_value=mock_response)

        element = await client.element_from_point(100, 200)

        assert element is not None
        assert element.element_id == "found-element-id"

    @pytest.mark.asyncio
    async def test_element_from_point_not_found(self):
        """Test returning None when no element at coordinates."""
        client = WinAppDriverClient()
        client.session_id = "test-session"
        client._client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"value": {}}
        client._client.post = AsyncMock(return_value=mock_response)

        element = await client.element_from_point(999, 999)

        assert element is None

    @pytest.mark.asyncio
    async def test_element_from_point_no_session(self):
        """Test element_from_point returns None without session."""
        client = WinAppDriverClient()

        element = await client.element_from_point(100, 200)

        assert element is None

    @pytest.mark.asyncio
    async def test_find_element_by_name(self):
        """Test finding element by Name property."""
        client = WinAppDriverClient()
        client.session_id = "test-session"
        client._client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": {LEGACY_ELEMENT_KEY: "named-element"}
        }
        client._client.post = AsyncMock(return_value=mock_response)

        element = await client.find_element_by_name("OK")

        assert element is not None
        assert element.element_id == "named-element"

    @pytest.mark.asyncio
    async def test_find_element_by_automation_id(self):
        """Test finding element by AutomationId."""
        client = WinAppDriverClient()
        client.session_id = "test-session"
        client._client = AsyncMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": {W3C_ELEMENT_KEY: "auto-element"}
        }
        client._client.post = AsyncMock(return_value=mock_response)

        element = await client.find_element_by_automation_id("btnSubmit")

        assert element is not None
        assert element.element_id == "auto-element"

    @pytest.mark.asyncio
    async def test_close_session(self):
        """Test session cleanup."""
        client = WinAppDriverClient()
        client.session_id = "test-session"
        client._client = AsyncMock()
        client._client.delete = AsyncMock()
        client._client.aclose = AsyncMock()

        await client.close_session()

        assert client.session_id is None
        assert client._client is None


class TestWindowsComputerFactory:
    """Tests for get_computer factory with Windows config."""

    def test_factory_returns_native_on_non_windows(self):
        """Test that non-Windows platforms get NativeComputer."""
        from deskpilot.cua_bridge.computer import NativeComputer, get_computer

        config = DeskPilotConfig()

        with patch("deskpilot.cua_bridge.computer.platform.system", return_value="Darwin"):
            computer = get_computer(config)
            assert isinstance(computer, NativeComputer)

    def test_factory_returns_windows_on_windows(self):
        """Test that Windows with WinAppDriver enabled gets WindowsComputer."""
        from deskpilot.cua_bridge.computer import WindowsComputer, get_computer

        config = DeskPilotConfig()

        with patch("deskpilot.cua_bridge.computer.platform.system", return_value="Windows"):
            computer = get_computer(config)
            assert isinstance(computer, WindowsComputer)

    def test_factory_returns_native_when_wad_disabled(self):
        """Test that Windows with WinAppDriver disabled gets NativeComputer."""
        from deskpilot.cua_bridge.computer import NativeComputer, get_computer

        config = DeskPilotConfig(
            windows=WindowsConfig(
                winappdriver=WinAppDriverConfig(enabled=False)
            )
        )

        with patch("deskpilot.cua_bridge.computer.platform.system", return_value="Windows"):
            computer = get_computer(config)
            assert isinstance(computer, NativeComputer)

    def test_factory_mock_mode_ignores_platform(self):
        """Test that mock mode always returns MockComputer."""
        from deskpilot.cua_bridge.computer import MockComputer, get_computer

        config = DeskPilotConfig()

        with patch("deskpilot.cua_bridge.computer.platform.system", return_value="Windows"):
            computer = get_computer(config, mock=True)
            assert isinstance(computer, MockComputer)


class TestWindowsComputerClickFallback:
    """Tests for WindowsComputer click with fallback behavior."""

    @pytest.mark.asyncio
    async def test_click_falls_back_when_no_element(self):
        """Test that click falls back to pyautogui when no element found."""
        from deskpilot.cua_bridge.computer import WindowsComputer

        config = DeskPilotConfig()
        computer = WindowsComputer(config)

        # Mock pyautogui and mss
        mock_pyautogui = MagicMock()
        mock_pyautogui.click = MagicMock()
        computer._pyautogui = mock_pyautogui
        computer._connected = True

        # Mock WinAppDriver returning no element
        mock_wad = AsyncMock()
        mock_wad.element_from_point = AsyncMock(return_value=None)
        computer._wad = mock_wad

        await computer.click(100, 200)

        # Should fall back to pyautogui
        mock_pyautogui.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_click_uses_winappdriver_when_element_found(self):
        """Test that click uses WinAppDriver element when found."""
        from deskpilot.cua_bridge.computer import WindowsComputer

        config = DeskPilotConfig()
        computer = WindowsComputer(config)

        mock_pyautogui = MagicMock()
        computer._pyautogui = mock_pyautogui
        computer._connected = True

        # Mock WinAppDriver finding an element
        mock_element = AsyncMock()
        mock_element.click = AsyncMock()
        mock_wad = AsyncMock()
        mock_wad.element_from_point = AsyncMock(return_value=mock_element)
        computer._wad = mock_wad

        await computer.click(100, 200)

        # Should use WinAppDriver element click, NOT pyautogui
        mock_element.click.assert_called_once()
        mock_pyautogui.click.assert_not_called()

    @pytest.mark.asyncio
    async def test_click_falls_back_on_wad_error(self):
        """Test fallback when WinAppDriver throws an error."""
        from deskpilot.cua_bridge.computer import WindowsComputer

        config = DeskPilotConfig()
        computer = WindowsComputer(config)

        mock_pyautogui = MagicMock()
        mock_pyautogui.click = MagicMock()
        computer._pyautogui = mock_pyautogui
        computer._connected = True

        # Mock WinAppDriver raising an error
        mock_wad = AsyncMock()
        mock_wad.element_from_point = AsyncMock(side_effect=RuntimeError("WAD error"))
        computer._wad = mock_wad

        await computer.click(100, 200)

        # Should fall back to pyautogui
        mock_pyautogui.click.assert_called_once()

    @pytest.mark.asyncio
    async def test_click_raises_when_fallback_disabled(self):
        """Test that errors propagate when fallback is disabled."""
        from deskpilot.cua_bridge.computer import WindowsComputer

        config = DeskPilotConfig(
            windows=WindowsConfig(fallback_on_failure=False)
        )
        computer = WindowsComputer(config)

        mock_pyautogui = MagicMock()
        computer._pyautogui = mock_pyautogui
        computer._connected = True

        mock_wad = AsyncMock()
        mock_wad.element_from_point = AsyncMock(side_effect=RuntimeError("WAD error"))
        computer._wad = mock_wad

        with pytest.raises(RuntimeError, match="WAD error"):
            await computer.click(100, 200)

    @pytest.mark.asyncio
    async def test_right_click_uses_pyautogui(self):
        """Test that right-click always uses pyautogui (not WinAppDriver)."""
        from deskpilot.cua_bridge.computer import WindowsComputer

        config = DeskPilotConfig()
        computer = WindowsComputer(config)

        mock_pyautogui = MagicMock()
        mock_pyautogui.click = MagicMock()
        computer._pyautogui = mock_pyautogui
        computer._connected = True

        mock_wad = AsyncMock()
        computer._wad = mock_wad

        await computer.click(100, 200, button="right")

        # Right-click should go directly to pyautogui
        mock_pyautogui.click.assert_called_once()
        mock_wad.element_from_point.assert_not_called()

    @pytest.mark.asyncio
    async def test_has_winappdriver_property(self):
        """Test has_winappdriver property."""
        from deskpilot.cua_bridge.computer import WindowsComputer

        config = DeskPilotConfig()
        computer = WindowsComputer(config)

        assert computer.has_winappdriver is False

        computer._wad = MagicMock()
        assert computer.has_winappdriver is True
