"""End-to-end tests for the Docker demo container.

These tests require:
1. Docker running
2. `make docker-run` to start the demo container
3. Playwright installed: pip install playwright && playwright install chromium

Run with: pytest tests/e2e/ -v --tb=short
"""

import os

import pytest

# Skip all tests if not in e2e mode
pytestmark = pytest.mark.skipif(
    os.environ.get("DESKPILOT_E2E") != "1",
    reason="E2E tests require DESKPILOT_E2E=1 and running Docker container",
)


@pytest.fixture
def browser_page():
    """Create a Playwright browser page."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not installed: pip install playwright")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


class TestDockerDemo:
    """Tests for the Docker demo noVNC interface."""

    def test_novnc_loads(self, browser_page):
        """Test that noVNC web interface loads."""
        page = browser_page

        # Navigate to noVNC interface
        page.goto("http://localhost:8006", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)

        # Take screenshot for inspection
        page.screenshot(path="/tmp/deskpilot_novnc.png", full_page=True)

        # noVNC should have a canvas or VNC-related elements
        # This validates the web interface is accessible
        content = page.content()
        assert "noVNC" in content or "vnc" in content.lower() or page.locator("canvas").count() > 0

    def test_novnc_connect_button(self, browser_page):
        """Test that noVNC has a connect interface."""
        page = browser_page

        page.goto("http://localhost:8006", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)

        # Look for connect/start button or VNC canvas
        buttons = page.locator("button").all()
        inputs = page.locator("input").all()

        # noVNC interface should have some interactive elements
        assert len(buttons) > 0 or len(inputs) > 0 or page.locator("canvas").count() > 0


class TestDemoScreenshot:
    """Screenshot-based validation of demo state."""

    def test_capture_demo_state(self, browser_page):
        """Capture screenshot of demo for manual inspection."""
        page = browser_page

        page.goto("http://localhost:8006", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)

        # Wait for potential VNC connection
        page.wait_for_timeout(3000)

        # Capture final state
        screenshot_path = "/tmp/deskpilot_demo_state.png"
        page.screenshot(path=screenshot_path, full_page=True)

        # Verify screenshot was created
        assert os.path.exists(screenshot_path)
        print(f"\nDemo screenshot saved to: {screenshot_path}")
