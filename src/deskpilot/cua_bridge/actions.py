"""High-level actions for computer control."""

from __future__ import annotations

import asyncio
import base64
import io
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

from deskpilot.cua_bridge.computer import BaseComputer
from deskpilot.wizard.config import DeskPilotConfig, get_config


@dataclass
class ScreenshotResult:
    """Result of a screenshot action."""

    image: Image.Image
    timestamp: datetime
    description: str | None = None
    path: Path | None = None

    def to_base64(self) -> str:
        """Convert image to base64 for API calls."""
        buffer = io.BytesIO()
        self.image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


@dataclass
class ActionResult:
    """Result of an action."""

    success: bool
    action: str
    details: dict | None = None
    error: str | None = None
    screenshot: ScreenshotResult | None = None


class Actions:
    """High-level actions for computer automation."""

    def __init__(
        self, computer: BaseComputer, config: DeskPilotConfig | None = None
    ) -> None:
        self.computer = computer
        self.config = config or get_config()
        self._screenshots_dir = Path(self.config.logging.screenshots_dir)

    async def screenshot(
        self,
        save: bool = False,
        describe: bool = False,
    ) -> ScreenshotResult:
        """Capture a screenshot.

        Args:
            save: Save screenshot to disk.
            describe: Generate AI description of the screen.

        Returns:
            ScreenshotResult with image and optional description.
        """
        image = await self.computer.screenshot()
        timestamp = datetime.now()

        result = ScreenshotResult(image=image, timestamp=timestamp)

        if save:
            self._screenshots_dir.mkdir(parents=True, exist_ok=True)
            filename = f"screenshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
            result.path = self._screenshots_dir / filename
            image.save(result.path)

        if describe:
            # Description will be done via the agent
            # For now, return without description
            result.description = None

        return result

    async def click(
        self,
        x: int | None = None,
        y: int | None = None,
        target: str | None = None,
        button: str = "left",
    ) -> ActionResult:
        """Click at coordinates or on a target element.

        Args:
            x: X coordinate (required if target not specified).
            y: Y coordinate (required if target not specified).
            target: Text/element to click on (uses AI vision to find).
            button: Mouse button ('left', 'right', 'middle').

        Returns:
            ActionResult indicating success/failure.
        """
        if target is not None:
            # Target-based clicking requires AI agent - return placeholder
            return ActionResult(
                success=False,
                action="click",
                error="Target-based clicking requires AI agent. Use coordinates or agent.run().",
            )

        if x is None or y is None:
            return ActionResult(
                success=False,
                action="click",
                error="Either coordinates (x, y) or target must be specified.",
            )

        try:
            await self.computer.click(x, y, button=button)
            return ActionResult(
                success=True,
                action="click",
                details={"x": x, "y": y, "button": button},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action="click",
                error=str(e),
            )

    async def double_click(self, x: int, y: int) -> ActionResult:
        """Double-click at coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            ActionResult indicating success/failure.
        """
        try:
            await self.computer.double_click(x, y)
            return ActionResult(
                success=True,
                action="double_click",
                details={"x": x, "y": y},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action="double_click",
                error=str(e),
            )

    async def type_text(self, text: str) -> ActionResult:
        """Type text into the currently focused element.

        Args:
            text: Text to type.

        Returns:
            ActionResult indicating success/failure.
        """
        try:
            await self.computer.type_text(text)
            return ActionResult(
                success=True,
                action="type_text",
                details={"text": text, "length": len(text)},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action="type_text",
                error=str(e),
            )

    async def press_key(self, key: str) -> ActionResult:
        """Press a keyboard key.

        Args:
            key: Key to press (e.g., 'enter', 'escape', 'tab').

        Returns:
            ActionResult indicating success/failure.
        """
        try:
            await self.computer.press_key(key)
            return ActionResult(
                success=True,
                action="press_key",
                details={"key": key},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action="press_key",
                error=str(e),
            )

    async def hotkey(self, *keys: str) -> ActionResult:
        """Press a key combination.

        Args:
            keys: Keys to press together (e.g., 'ctrl', 'c').

        Returns:
            ActionResult indicating success/failure.
        """
        try:
            await self.computer.hotkey(*keys)
            return ActionResult(
                success=True,
                action="hotkey",
                details={"keys": list(keys)},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action="hotkey",
                error=str(e),
            )

    async def launch(self, app: str) -> ActionResult:
        """Launch an application.

        On Windows, this uses the Start menu search.
        On other platforms, behavior varies.

        Args:
            app: Application name to launch.

        Returns:
            ActionResult indicating success/failure.
        """
        try:
            # Windows: Open Start menu and search
            # Press Windows key
            await self.computer.press_key("win")
            await asyncio.sleep(0.5)

            # Type app name
            await self.computer.type_text(app)
            await asyncio.sleep(0.3)

            # Press Enter to launch
            await self.computer.press_key("enter")
            await asyncio.sleep(1.0)  # Wait for app to start

            return ActionResult(
                success=True,
                action="launch",
                details={"app": app},
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action="launch",
                error=str(e),
            )

    async def wait(self, seconds: float) -> ActionResult:
        """Wait for a specified time.

        Args:
            seconds: Time to wait.

        Returns:
            ActionResult indicating success.
        """
        await asyncio.sleep(seconds)
        return ActionResult(
            success=True,
            action="wait",
            details={"seconds": seconds},
        )


async def create_actions(mock: bool = False) -> Actions:
    """Create and initialize an Actions instance.

    Args:
        mock: If True, use MockComputer for testing.

    Returns:
        Connected Actions instance.
    """
    from deskpilot.cua_bridge.computer import get_computer

    config = get_config()
    computer = get_computer(config, mock=mock)
    await computer.connect()

    return Actions(computer, config)
