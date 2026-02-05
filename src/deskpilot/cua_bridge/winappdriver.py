"""WinAppDriver REST API client for Windows UI Automation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# W3C WebDriver element identifier key
W3C_ELEMENT_KEY = "element-6066-11e4-a52e-4f735466cecf"
# Legacy JsonWireProtocol element key (WinAppDriver uses this)
LEGACY_ELEMENT_KEY = "ELEMENT"


@dataclass
class WinElement:
    """Represents a Windows UI element found via WinAppDriver."""

    session: WinAppDriverClient
    element_id: str

    async def click(self) -> None:
        """Click the element via UI Automation."""
        await self.session._post(f"element/{self.element_id}/click")

    async def double_click(self) -> None:
        """Double-click the element using the W3C Actions API."""
        actions = {
            "actions": [
                {
                    "type": "pointer",
                    "id": "mouse",
                    "actions": [
                        {
                            "type": "pointerMove",
                            "origin": {W3C_ELEMENT_KEY: self.element_id},
                        },
                        {"type": "pointerDown", "button": 0},
                        {"type": "pointerUp", "button": 0},
                        {"type": "pause", "duration": 50},
                        {"type": "pointerDown", "button": 0},
                        {"type": "pointerUp", "button": 0},
                    ],
                }
            ]
        }
        await self.session._post("actions", json=actions)

    async def get_attribute(self, name: str) -> str | None:
        """Get an element attribute (e.g., Name, AutomationId, ClassName)."""
        data = await self.session._get(f"element/{self.element_id}/attribute/{name}")
        return data.get("value")

    async def get_tag_name(self) -> str:
        """Get the element's control type (e.g., Button, Edit, Window)."""
        data = await self.session._get(f"element/{self.element_id}/name")
        return data.get("value", "")


class WinAppDriverClient:
    """Async client for the WinAppDriver REST API.

    WinAppDriver implements the W3C WebDriver protocol and provides
    access to Windows UI Automation elements. This client creates a
    Root desktop session for desktop-wide element discovery.
    """

    def __init__(self, port: int = 4723, timeout: float = 10.0) -> None:
        self.base_url = f"http://127.0.0.1:{port}"
        self.timeout = timeout
        self.session_id: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def create_session(self) -> None:
        """Create a Root session for desktop-wide automation."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

        # Root session gives access to the entire desktop
        payload = {
            "capabilities": {
                "alwaysMatch": {
                    "platformName": "Windows",
                    "appium:app": "Root",
                    "appium:deviceName": "WindowsPC",
                }
            }
        }

        response = await self._client.post("/session", json=payload)
        response.raise_for_status()
        data = response.json()
        self.session_id = data["value"]["sessionId"]
        logger.info("WinAppDriver session created: %s", self.session_id)

    async def element_from_point(self, x: int, y: int) -> WinElement | None:
        """Find the UI element at the given screen coordinates.

        Uses WinAppDriver's coordinate-based element search. This queries
        the Windows UI Automation tree to find which element occupies the
        given point on screen.

        Returns None if no element is found (falls through to pyautogui).
        """
        if not self._client or not self.session_id:
            return None

        # Strategy: use runtime_id-based search via the touch/click endpoint
        # WinAppDriver supports finding elements at coordinates through
        # the /session/{id}/element endpoint with various strategies.
        # We use the "xpath" strategy with BoundingRectangle filtering.
        #
        # Alternative approach: use Windows API ElementFromPoint directly
        # by executing a script, then find the element in the session.
        try:
            # First attempt: use coordinate-based click target resolution
            # WinAppDriver's touch/click endpoint resolves the element at coords
            payload = {
                "using": "xpath",
                "value": f"//*[contains(@BoundingRectangle, '{x}') "
                f"and contains(@BoundingRectangle, '{y}')]",
            }

            response = await self._client.post(
                f"/session/{self.session_id}/element",
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                value = data.get("value", {})
                element_id = value.get(LEGACY_ELEMENT_KEY) or value.get(
                    W3C_ELEMENT_KEY
                )
                if element_id:
                    logger.debug("Found element at (%d, %d): %s", x, y, element_id)
                    return WinElement(session=self, element_id=element_id)

            logger.debug("No element found at (%d, %d)", x, y)
        except (httpx.HTTPError, KeyError) as e:
            logger.debug("Element lookup failed at (%d, %d): %s", x, y, e)

        return None

    async def find_element_by_name(self, name: str) -> WinElement | None:
        """Find an element by its Name property."""
        return await self._find_element("name", name)

    async def find_element_by_automation_id(
        self, automation_id: str
    ) -> WinElement | None:
        """Find an element by its AutomationId."""
        return await self._find_element("accessibility id", automation_id)

    async def _find_element(
        self, strategy: str, value: str
    ) -> WinElement | None:
        """Find an element using the given locator strategy."""
        if not self._client or not self.session_id:
            return None

        try:
            payload = {"using": strategy, "value": value}
            response = await self._client.post(
                f"/session/{self.session_id}/element",
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                val = data.get("value", {})
                element_id = val.get(LEGACY_ELEMENT_KEY) or val.get(W3C_ELEMENT_KEY)
                if element_id:
                    return WinElement(session=self, element_id=element_id)
        except (httpx.HTTPError, KeyError) as e:
            logger.debug("Find element failed (%s=%s): %s", strategy, value, e)

        return None

    async def close_session(self) -> None:
        """Close the WinAppDriver session and release resources."""
        if self._client and self.session_id:
            try:
                await self._client.delete(f"/session/{self.session_id}")
            except httpx.HTTPError:
                pass  # Session may already be gone
            finally:
                await self._client.aclose()
                self._client = None
                self.session_id = None
                logger.info("WinAppDriver session closed")

    async def _post(self, path: str, json: dict | None = None) -> dict[str, Any]:
        """POST to a session endpoint."""
        if not self._client or not self.session_id:
            raise RuntimeError("No active WinAppDriver session")

        response = await self._client.post(
            f"/session/{self.session_id}/{path}",
            json=json or {},
        )
        response.raise_for_status()
        return response.json()

    async def _get(self, path: str) -> dict[str, Any]:
        """GET from a session endpoint."""
        if not self._client or not self.session_id:
            raise RuntimeError("No active WinAppDriver session")

        response = await self._client.get(
            f"/session/{self.session_id}/{path}",
        )
        response.raise_for_status()
        return response.json()
