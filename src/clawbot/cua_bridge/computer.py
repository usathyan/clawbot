"""Computer abstraction for VM and Native modes."""

from __future__ import annotations

import asyncio
import platform
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clawbot.wizard.config import ClawBotConfig, get_config

if TYPE_CHECKING:
    from PIL import Image


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


class VMComputer(BaseComputer):
    """Computer control via Cua VM (Docker + QEMU)."""

    def __init__(self, config: ClawBotConfig) -> None:
        self.config = config
        self._computer = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to the Cua VM."""
        try:
            from computer import Computer
        except ImportError as e:
            raise ImportError(
                "cua-agent package not installed. Run: uv pip install cua-agent"
            ) from e

        self._computer = Computer(
            os_type="windows",
            provider_type="docker",
            name=self.config.vm.image,
        )
        # Cua Computer connects automatically when used
        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from the VM."""
        if self._computer:
            # Cua handles cleanup automatically
            self._computer = None
        self._connected = False

    async def screenshot(self) -> Image.Image:
        """Capture screenshot from VM."""
        if not self._computer:
            raise RuntimeError("Not connected to VM")
        return await self._computer.screenshot()

    async def click(self, x: int, y: int, button: str = "left") -> None:
        """Click in VM."""
        if not self._computer:
            raise RuntimeError("Not connected to VM")
        await self._computer.click(x, y, button=button)

    async def double_click(self, x: int, y: int) -> None:
        """Double-click in VM."""
        if not self._computer:
            raise RuntimeError("Not connected to VM")
        await self._computer.double_click(x, y)

    async def type_text(self, text: str) -> None:
        """Type text in VM."""
        if not self._computer:
            raise RuntimeError("Not connected to VM")
        await self._computer.type(text)

    async def press_key(self, key: str) -> None:
        """Press key in VM."""
        if not self._computer:
            raise RuntimeError("Not connected to VM")
        await self._computer.press(key)

    async def hotkey(self, *keys: str) -> None:
        """Press hotkey in VM."""
        if not self._computer:
            raise RuntimeError("Not connected to VM")
        await self._computer.hotkey(*keys)

    def get_screen_info(self) -> ScreenInfo:
        """Get VM screen info."""
        # Default Windows VM resolution
        return ScreenInfo(width=1920, height=1080)

    @property
    def is_connected(self) -> bool:
        return self._connected


class NativeComputer(BaseComputer):
    """Computer control via native OS APIs (pyautogui + mss)."""

    def __init__(self, config: ClawBotConfig) -> None:
        self.config = config
        self._connected = False
        self._pyautogui = None
        self._mss = None

    async def connect(self) -> None:
        """Initialize native control libraries."""
        if platform.system() != "Windows":
            # Allow connection for testing, but warn
            import warnings

            warnings.warn(
                f"Native mode is designed for Windows, running on {platform.system()}. "
                "Some features may not work correctly."
            )

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
                "Run: uv pip install -e '.[native]'"
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


class MockComputer(BaseComputer):
    """Mock computer for testing without actual VM or native control."""

    def __init__(self, config: ClawBotConfig) -> None:
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


def get_computer(config: ClawBotConfig | None = None, mock: bool = False) -> BaseComputer:
    """Factory function to create appropriate Computer instance.

    Args:
        config: Configuration. If None, loads from default locations.
        mock: If True, return MockComputer for testing.

    Returns:
        BaseComputer instance based on deployment mode.
    """
    if config is None:
        config = get_config()

    if mock:
        return MockComputer(config)

    if config.deployment.mode == "vm":
        return VMComputer(config)
    elif config.deployment.mode == "native":
        return NativeComputer(config)
    else:
        raise ValueError(f"Unknown deployment mode: {config.deployment.mode}")
