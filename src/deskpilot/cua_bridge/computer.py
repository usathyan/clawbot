"""Computer abstraction for native desktop control."""

from __future__ import annotations

import asyncio
import logging
import platform
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from deskpilot.wizard.config import DeskPilotConfig, get_config

if TYPE_CHECKING:
    from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class ScreenInfo:
    """Screen information."""

    width: int
    height: int
    scale: float = 1.0


class BaseComputer(ABC):
    """Abstract base class for computer control."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the computer."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the computer."""
        pass

    @abstractmethod
    async def screenshot(self) -> Image.Image:
        """Capture a screenshot."""
        pass

    @abstractmethod
    async def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at coordinates."""
        pass

    @abstractmethod
    async def double_click(self, x: int, y: int) -> None:
        """Double-click at coordinates."""
        pass

    @abstractmethod
    async def type_text(self, text: str) -> None:
        """Type text."""
        pass

    @abstractmethod
    async def press_key(self, key: str) -> None:
        """Press a key (e.g., 'enter', 'escape')."""
        pass

    @abstractmethod
    async def hotkey(self, *keys: str) -> None:
        """Press a key combination (e.g., 'ctrl', 'c')."""
        pass

    @abstractmethod
    def get_screen_info(self) -> ScreenInfo:
        """Get screen dimensions."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected."""
        pass


class NativeComputer(BaseComputer):
    """Computer control via native OS APIs (pyautogui + mss)."""

    def __init__(self, config: DeskPilotConfig) -> None:
        self.config = config
        self._connected = False
        self._pyautogui = None
        self._mss = None

    async def connect(self) -> None:
        """Initialize native control libraries."""
        try:
            import mss
            import pyautogui

            self._pyautogui = pyautogui
            self._mss = mss.mss()

            # Configure pyautogui
            pyautogui.PAUSE = self.config.native.click_pause
            pyautogui.FAILSAFE = True

            self._connected = True
        except ImportError as e:
            raise ImportError(
                "Native mode requires pyautogui and mss. "
                "Run: pip install deskpilot[native] or pip install pyautogui mss pillow"
            ) from e

    async def disconnect(self) -> None:
        """Cleanup native resources."""
        if self._mss:
            self._mss.close()
            self._mss = None
        self._pyautogui = None
        self._connected = False

    async def screenshot(self) -> Image.Image:
        """Capture screenshot of primary monitor."""
        if not self._mss:
            raise RuntimeError("Not connected")

        from PIL import Image

        # Run in thread to avoid blocking
        def capture():
            monitor = self._mss.monitors[1]  # Primary monitor
            sct_img = self._mss.grab(monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        return await asyncio.to_thread(capture)

    async def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at screen coordinates."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")
        await asyncio.to_thread(self._pyautogui.click, x, y, button=button)

    async def double_click(self, x: int, y: int) -> None:
        """Double-click at coordinates."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")
        await asyncio.to_thread(self._pyautogui.doubleClick, x, y)

    async def type_text(self, text: str) -> None:
        """Type text with configured interval."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")
        await asyncio.to_thread(
            self._pyautogui.write, text, interval=self.config.native.typing_interval
        )

    async def press_key(self, key: str) -> None:
        """Press a single key."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")
        await asyncio.to_thread(self._pyautogui.press, key)

    async def hotkey(self, *keys: str) -> None:
        """Press a key combination."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")
        await asyncio.to_thread(self._pyautogui.hotkey, *keys)

    def get_screen_info(self) -> ScreenInfo:
        """Get primary monitor dimensions."""
        if not self._mss:
            raise RuntimeError("Not connected")
        monitor = self._mss.monitors[1]
        return ScreenInfo(width=monitor["width"], height=monitor["height"])

    @property
    def is_connected(self) -> bool:
        return self._connected


class WindowsComputer(BaseComputer):
    """Windows desktop control via WinAppDriver + pyautogui fallback.

    Uses WinAppDriver (Windows UI Automation APIs) for click operations
    to get element-based accuracy, with pyautogui as a fallback when
    no element is found. Screenshots and keyboard input still use
    pyautogui/mss for speed.
    """

    def __init__(self, config: DeskPilotConfig) -> None:
        self.config = config
        self._connected = False
        self._wad = None  # WinAppDriverClient
        self._wad_process: subprocess.Popen | None = None
        self._pyautogui = None
        self._mss = None

    async def connect(self) -> None:
        """Initialize WinAppDriver and fallback libraries."""
        try:
            import mss
            import pyautogui

            self._pyautogui = pyautogui
            self._mss = mss.mss()
            pyautogui.PAUSE = self.config.windows.click_pause
            pyautogui.FAILSAFE = True
        except ImportError as e:
            raise ImportError(
                "Windows mode requires pyautogui and mss. "
                "Run: pip install deskpilot"
            ) from e

        # Start WinAppDriver if configured
        wad_config = self.config.windows.winappdriver
        if wad_config.enabled:
            from deskpilot.cua_bridge.winappdriver import WinAppDriverClient

            if wad_config.auto_start:
                self._wad_process = await self._start_winappdriver()

            self._wad = WinAppDriverClient(
                port=wad_config.port,
                timeout=wad_config.timeout,
            )
            try:
                await self._wad.create_session()
                logger.info("WinAppDriver connected on port %d", wad_config.port)
            except Exception as e:
                logger.warning("WinAppDriver unavailable, using pyautogui only: %s", e)
                self._wad = None

        self._connected = True

    async def disconnect(self) -> None:
        """Cleanup all resources."""
        if self._wad:
            await self._wad.close_session()
            self._wad = None

        if self._wad_process:
            self._wad_process.terminate()
            self._wad_process.wait(timeout=5)
            self._wad_process = None

        if self._mss:
            self._mss.close()
            self._mss = None

        self._pyautogui = None
        self._connected = False

    async def screenshot(self) -> Image.Image:
        """Capture screenshot via mss (fast)."""
        if not self._mss:
            raise RuntimeError("Not connected")

        from PIL import Image

        def capture():
            monitor = self._mss.monitors[1]
            sct_img = self._mss.grab(monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        return await asyncio.to_thread(capture)

    async def click(self, x: int, y: int, button: str = "left") -> None:
        """Click using WinAppDriver element detection with pyautogui fallback."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")

        # Try WinAppDriver for left-clicks when available
        if button == "left" and self._wad:
            try:
                element = await self._wad.element_from_point(x, y)
                if element:
                    await element.click()
                    logger.debug("WinAppDriver click at (%d, %d)", x, y)
                    return
            except Exception as e:
                if not self.config.windows.fallback_on_failure:
                    raise
                logger.debug("WinAppDriver click failed, falling back: %s", e)

        # Fallback to pyautogui coordinate-based click
        await asyncio.to_thread(self._pyautogui.click, x, y, button=button)

    async def double_click(self, x: int, y: int) -> None:
        """Double-click using WinAppDriver with pyautogui fallback."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")

        if self._wad:
            try:
                element = await self._wad.element_from_point(x, y)
                if element:
                    await element.double_click()
                    return
            except Exception as e:
                if not self.config.windows.fallback_on_failure:
                    raise
                logger.debug("WinAppDriver double_click failed, falling back: %s", e)

        await asyncio.to_thread(self._pyautogui.doubleClick, x, y)

    async def type_text(self, text: str) -> None:
        """Type via pyautogui."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")
        await asyncio.to_thread(
            self._pyautogui.write, text, interval=self.config.windows.typing_interval
        )

    async def press_key(self, key: str) -> None:
        """Press key via pyautogui."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")
        await asyncio.to_thread(self._pyautogui.press, key)

    async def hotkey(self, *keys: str) -> None:
        """Key combination via pyautogui."""
        if not self._pyautogui:
            raise RuntimeError("Not connected")
        await asyncio.to_thread(self._pyautogui.hotkey, *keys)

    def get_screen_info(self) -> ScreenInfo:
        """Get primary monitor dimensions."""
        if not self._mss:
            raise RuntimeError("Not connected")
        monitor = self._mss.monitors[1]
        return ScreenInfo(width=monitor["width"], height=monitor["height"])

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def has_winappdriver(self) -> bool:
        """Check if WinAppDriver is active (not just pyautogui fallback)."""
        return self._wad is not None

    async def _start_winappdriver(self) -> subprocess.Popen | None:
        """Start WinAppDriver.exe process."""
        wad_path = Path(self.config.windows.winappdriver.path)
        if not wad_path.exists():
            logger.warning(
                "WinAppDriver not found at %s. Run 'deskpilot install' to install it.",
                wad_path,
            )
            return None

        process = subprocess.Popen(
            [str(wad_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for WinAppDriver to be ready
        await asyncio.sleep(1)
        return process


class MockComputer(BaseComputer):
    """Mock computer for testing without actual native control."""

    def __init__(self, config: DeskPilotConfig) -> None:
        self.config = config
        self._connected = False
        self.actions: list[dict] = []  # Record actions for testing

    async def connect(self) -> None:
        self._connected = True
        self.actions.append({"action": "connect"})

    async def disconnect(self) -> None:
        self._connected = False
        self.actions.append({"action": "disconnect"})

    async def screenshot(self) -> Image.Image:
        from PIL import Image

        self.actions.append({"action": "screenshot"})
        # Return a blank image
        return Image.new("RGB", (1920, 1080), color=(50, 50, 50))

    async def click(self, x: int, y: int, button: str = "left") -> None:
        self.actions.append({"action": "click", "x": x, "y": y, "button": button})

    async def double_click(self, x: int, y: int) -> None:
        self.actions.append({"action": "double_click", "x": x, "y": y})

    async def type_text(self, text: str) -> None:
        self.actions.append({"action": "type_text", "text": text})

    async def press_key(self, key: str) -> None:
        self.actions.append({"action": "press_key", "key": key})

    async def hotkey(self, *keys: str) -> None:
        self.actions.append({"action": "hotkey", "keys": keys})

    def get_screen_info(self) -> ScreenInfo:
        return ScreenInfo(width=1920, height=1080)

    @property
    def is_connected(self) -> bool:
        return self._connected


def get_computer(config: DeskPilotConfig | None = None, mock: bool = False) -> BaseComputer:
    """Factory function to create appropriate Computer instance.

    On Windows with WinAppDriver enabled, returns WindowsComputer
    (WinAppDriver + pyautogui fallback). Otherwise returns NativeComputer
    (pyautogui + mss only).

    Args:
        config: Configuration. If None, loads from default locations.
        mock: If True, return MockComputer for testing.

    Returns:
        BaseComputer instance.
    """
    if config is None:
        config = get_config()

    if mock:
        return MockComputer(config)

    # Use WindowsComputer on Windows when WinAppDriver is enabled
    if platform.system() == "Windows" and config.windows.winappdriver.enabled:
        return WindowsComputer(config)

    return NativeComputer(config)
