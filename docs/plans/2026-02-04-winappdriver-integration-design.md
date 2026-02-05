# WinAppDriver Integration Design

**Date:** 2026-02-04
**Status:** Ready for implementation
**Target:** SimCyp Simulator and Windows desktop applications

---

## Overview

Integrate Microsoft WinAppDriver into DeskPilot for high-accuracy click operations on Windows. WinAppDriver uses Windows UI Automation APIs to interact with elements by their properties rather than raw pixel coordinates.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  DeskPilot Windows Edition                                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  AI Agent (Ollama + qwen2.5)                             │   │
│  │  Analyzes screenshot → outputs (x, y) coordinates        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  WindowsComputer                                          │   │
│  │                                                           │   │
│  │  click(x, y)                                              │   │
│  │      │                                                    │   │
│  │      ▼                                                    │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ WinAppDriver.element_from_point(x, y)               │ │   │
│  │  │     │                                               │ │   │
│  │  │     ├─► Element found → element.Click() ─► DONE     │ │   │
│  │  │     │                                               │ │   │
│  │  │     └─► No element / error                          │ │   │
│  │  │             │                                       │ │   │
│  │  │             ▼                                       │ │   │
│  │  │         pyautogui.click(x, y) ─► DONE (fallback)    │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                           │   │
│  │  screenshot() ──► mss (fast)                             │   │
│  │  type_text()  ──► pyautogui                              │   │
│  │  press_key()  ──► pyautogui                              │   │
│  │  hotkey()     ──► pyautogui                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Modes

### Development (macOS with Docker)

```
┌─────────────────────────────────────────────────────────────────┐
│  macOS Host                                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Docker Container (Windows 11 VM)                         │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  • WinAppDriver (installed)                         │  │  │
│  │  │  • DeskPilot (installed)                            │  │  │
│  │  │  • Ollama + qwen2.5:3b                              │  │  │
│  │  │  • Test apps: Calculator, Notepad                   │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                        │                                  │  │
│  │                  VNC (port 5901)                          │  │
│  └────────────────────────┼──────────────────────────────────┘  │
│                           ▼                                      │
│                    Browser: localhost:8006                       │
└─────────────────────────────────────────────────────────────────┘
```

### Production (Native Windows)

```
┌─────────────────────────────────────────────────────────────────┐
│  Windows PC                                                      │
│                                                                  │
│  $ deskpilot install                                            │
│      ✓ Enabling Developer Mode...                               │
│      ✓ Installing WinAppDriver...                               │
│      ✓ Installing Ollama...                                     │
│      ✓ Pulling qwen2.5:3b model...                              │
│      ✓ Installing OpenClaw...                                   │
│      ✓ Ready!                                                   │
│                                                                  │
│  $ deskpilot tui                                                │
│  > Open SimCyp and run a simulation                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Integration** | Hybrid fallback | Best accuracy with universal fallback |
| **Click mechanism** | element.Click() | More reliable than coordinates if window shifts |
| **Scope** | Click operations only | Keyboard works fine with pyautogui |
| **Screenshots** | mss (not WinAppDriver) | mss is faster |
| **Platform** | Windows-only | Simplifies implementation, add others later |
| **WinAppDriver lifecycle** | Auto-managed | Start on connect, stop on disconnect |
| **Installation** | Single script | Same install.ps1 for Docker VM and native |

---

## File Changes

### New Files

| File | Purpose |
|------|---------|
| `src/deskpilot/cua_bridge/winappdriver.py` | WinAppDriver REST API client |
| `src/deskpilot/installer/winappdriver.py` | Download/install/manage WinAppDriver |
| `docker/docker-compose.yml` | Windows VM for development |
| `docker/setup-vm.ps1` | First-time VM provisioning |
| `tests/e2e/test_winappdriver.py` | E2E tests for WinAppDriver |

### Modified Files

| File | Changes |
|------|---------|
| `src/deskpilot/cua_bridge/computer.py` | Replace NativeComputer with WindowsComputer |
| `src/deskpilot/wizard/config.py` | Add WinAppDriver config section |
| `src/deskpilot/installer/native.py` | Rename to windows.py, add WinAppDriver |
| `scripts/install.ps1` | Add WinAppDriver installation steps |
| `config/default.yaml` | Add windows.winappdriver settings |
| `pyproject.toml` | Add aiohttp dependency |

### Removed Files

| File | Reason |
|------|--------|
| `scripts/install.sh` | Windows-only (removed Mac/Linux) |

---

## Configuration

```yaml
# config/default.yaml
model:
  provider: ollama
  name: qwen2.5:3b
  base_url: http://localhost:11434

agent:
  max_steps: 50
  screenshot_on_step: true
  verbose: true

windows:
  winappdriver:
    enabled: true
    path: "C:\\Program Files\\Windows Application Driver\\WinAppDriver.exe"
    port: 4723
    auto_start: true
    timeout: 10
  screenshot_delay: 0.5
  typing_interval: 0.05
  click_pause: 0.1
  fallback_on_failure: true

openclaw:
  enabled: true
  skill_path: ~/.openclaw/skills/computer-use

logging:
  level: INFO
  screenshots_dir: ./screenshots
```

---

## Implementation Details

### WindowsComputer Class

```python
# src/deskpilot/cua_bridge/computer.py

class WindowsComputer(BaseComputer):
    """Windows desktop control via WinAppDriver + pyautogui fallback."""

    def __init__(self, config: DeskPilotConfig):
        self.config = config
        self._connected = False
        self._wad: WinAppDriverClient | None = None
        self._wad_process: subprocess.Popen | None = None
        self._pyautogui = None
        self._mss = None

    async def connect(self) -> None:
        """Initialize WinAppDriver and fallback libraries."""
        import mss
        import pyautogui

        # Start WinAppDriver if auto_start enabled
        if self.config.windows.winappdriver.auto_start:
            self._wad_process = await self._start_winappdriver()

        # Connect to WinAppDriver
        self._wad = WinAppDriverClient(
            port=self.config.windows.winappdriver.port,
            timeout=self.config.windows.winappdriver.timeout
        )
        await self._wad.create_session()

        # Initialize fallback
        self._pyautogui = pyautogui
        self._mss = mss.mss()
        pyautogui.PAUSE = self.config.windows.click_pause
        pyautogui.FAILSAFE = True

        self._connected = True

    async def disconnect(self) -> None:
        """Cleanup resources."""
        if self._wad:
            await self._wad.close_session()
            self._wad = None

        if self._wad_process:
            self._wad_process.terminate()
            self._wad_process = None

        if self._mss:
            self._mss.close()
            self._mss = None

        self._pyautogui = None
        self._connected = False

    async def click(self, x: int, y: int, button: str = "left") -> None:
        """Click using WinAppDriver element detection with pyautogui fallback."""
        # WinAppDriver only supports left-click via element
        if button == "left" and self._wad:
            try:
                element = await self._wad.element_from_point(x, y)
                if element:
                    await element.click()
                    return
            except Exception:
                if not self.config.windows.fallback_on_failure:
                    raise
                # Fall through to pyautogui

        # Fallback to coordinate-based click
        await asyncio.to_thread(self._pyautogui.click, x, y, button=button)

    async def double_click(self, x: int, y: int) -> None:
        """Double-click using WinAppDriver with pyautogui fallback."""
        if self._wad:
            try:
                element = await self._wad.element_from_point(x, y)
                if element:
                    await element.double_click()
                    return
            except Exception:
                if not self.config.windows.fallback_on_failure:
                    raise

        await asyncio.to_thread(self._pyautogui.doubleClick, x, y)

    async def screenshot(self) -> Image.Image:
        """Capture screenshot via mss (fast)."""
        from PIL import Image

        def capture():
            monitor = self._mss.monitors[1]
            sct_img = self._mss.grab(monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        return await asyncio.to_thread(capture)

    async def type_text(self, text: str) -> None:
        """Type via pyautogui."""
        await asyncio.to_thread(
            self._pyautogui.write, text,
            interval=self.config.windows.typing_interval
        )

    async def press_key(self, key: str) -> None:
        """Press key via pyautogui."""
        await asyncio.to_thread(self._pyautogui.press, key)

    async def hotkey(self, *keys: str) -> None:
        """Key combination via pyautogui."""
        await asyncio.to_thread(self._pyautogui.hotkey, *keys)

    async def _start_winappdriver(self) -> subprocess.Popen:
        """Start WinAppDriver.exe process."""
        wad_path = self.config.windows.winappdriver.path
        if not Path(wad_path).exists():
            raise FileNotFoundError(
                f"WinAppDriver not found at {wad_path}. "
                "Run 'deskpilot install' to install it."
            )

        process = subprocess.Popen(
            [wad_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for WinAppDriver to be ready
        await asyncio.sleep(1)
        return process
```

### WinAppDriver Client

```python
# src/deskpilot/cua_bridge/winappdriver.py

import aiohttp
from dataclasses import dataclass

@dataclass
class WinElement:
    """Represents a Windows UI element."""
    session: "WinAppDriverClient"
    element_id: str

    async def click(self) -> None:
        """Click the element."""
        await self.session._post(f"element/{self.element_id}/click")

    async def double_click(self) -> None:
        """Double-click the element."""
        # WinAppDriver uses Actions API for double-click
        actions = {
            "actions": [{
                "type": "pointer",
                "id": "mouse",
                "actions": [
                    {"type": "pointerMove", "origin": {"element-6066-11e4-a52e-4f735466cecf": self.element_id}},
                    {"type": "pointerDown", "button": 0},
                    {"type": "pointerUp", "button": 0},
                    {"type": "pause", "duration": 50},
                    {"type": "pointerDown", "button": 0},
                    {"type": "pointerUp", "button": 0}
                ]
            }]
        }
        await self.session._post("actions", json=actions)


class WinAppDriverClient:
    """Async client for WinAppDriver REST API."""

    def __init__(self, port: int = 4723, timeout: int = 10):
        self.base_url = f"http://127.0.0.1:{port}"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session_id: str | None = None
        self._http: aiohttp.ClientSession | None = None

    async def create_session(self) -> None:
        """Create a Root session for desktop-wide automation."""
        self._http = aiohttp.ClientSession(timeout=self.timeout)

        payload = {
            "capabilities": {
                "alwaysMatch": {
                    "platformName": "Windows",
                    "appium:app": "Root",
                    "appium:deviceName": "WindowsPC"
                }
            }
        }

        async with self._http.post(
            f"{self.base_url}/session",
            json=payload
        ) as resp:
            data = await resp.json()
            self.session_id = data["value"]["sessionId"]

    async def element_from_point(self, x: int, y: int) -> WinElement | None:
        """Find UI element at screen coordinates using UI Automation."""
        # Use XPath with runtime ID based on coordinates
        # WinAppDriver can find elements via coordinate-based search

        # First, get the element at the point using Windows API via PowerShell
        # Then find it in WinAppDriver by its properties

        # Alternative: Use the /session/{id}/element with location strategy
        payload = {
            "using": "xpath",
            "value": f"//*[contains(@BoundingRectangle, '{x}') and contains(@BoundingRectangle, '{y}')]"
        }

        try:
            async with self._http.post(
                f"{self.base_url}/session/{self.session_id}/element",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    element_id = data["value"]["ELEMENT"]
                    return WinElement(session=self, element_id=element_id)
        except Exception:
            pass

        return None

    async def close_session(self) -> None:
        """Close the WinAppDriver session."""
        if self._http and self.session_id:
            await self._http.delete(f"{self.base_url}/session/{self.session_id}")
            await self._http.close()
            self._http = None
            self.session_id = None

    async def _post(self, path: str, json: dict = None) -> dict:
        """POST request to WinAppDriver."""
        async with self._http.post(
            f"{self.base_url}/session/{self.session_id}/{path}",
            json=json or {}
        ) as resp:
            return await resp.json()
```

### Installation Script Updates

```powershell
# scripts/install.ps1 - Add WinAppDriver installation

function Install-WinAppDriver {
    Write-Host "Installing WinAppDriver..." -ForegroundColor Blue

    $wadPath = "C:\Program Files\Windows Application Driver\WinAppDriver.exe"

    if (Test-Path $wadPath) {
        Write-Host "  WinAppDriver already installed" -ForegroundColor Green
        return
    }

    # Download WinAppDriver
    $wadUrl = "https://github.com/microsoft/WinAppDriver/releases/download/v1.2.1/WindowsApplicationDriver_1.2.1.msi"
    $wadInstaller = "$env:TEMP\WinAppDriver.msi"

    Write-Host "  Downloading WinAppDriver..."
    Invoke-WebRequest -Uri $wadUrl -OutFile $wadInstaller

    # Install silently
    Write-Host "  Running installer..."
    Start-Process msiexec.exe -ArgumentList "/i", $wadInstaller, "/quiet", "/norestart" -Wait

    Remove-Item $wadInstaller -Force
    Write-Host "  WinAppDriver installed" -ForegroundColor Green
}

function Enable-DeveloperMode {
    Write-Host "Checking Developer Mode..." -ForegroundColor Blue

    $devMode = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Name "AllowDevelopmentWithoutDevLicense" -ErrorAction SilentlyContinue

    if ($devMode.AllowDevelopmentWithoutDevLicense -eq 1) {
        Write-Host "  Developer Mode already enabled" -ForegroundColor Green
        return
    }

    Write-Host "  Developer Mode is required for WinAppDriver." -ForegroundColor Yellow
    $confirm = Read-Host "  Enable Developer Mode? (Y/n)"

    if ($confirm -eq "" -or $confirm -eq "Y" -or $confirm -eq "y") {
        # Requires admin
        Start-Process powershell -Verb RunAs -ArgumentList "-Command", "reg add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock' /v AllowDevelopmentWithoutDevLicense /t REG_DWORD /d 1 /f" -Wait
        Write-Host "  Developer Mode enabled" -ForegroundColor Green
    } else {
        Write-Host "  Skipped. WinAppDriver may not work properly." -ForegroundColor Yellow
    }
}
```

---

## Docker Setup

```yaml
# docker/docker-compose.yml
services:
  deskpilot-dev:
    image: dockurr/windows:latest
    container_name: deskpilot-windows
    environment:
      VERSION: "11"
      RAM_SIZE: "8G"
      CPU_CORES: "4"
      KVM: "N"
    ports:
      - "5901:5900"
      - "8006:8006"
    volumes:
      - ../scripts:/shared:ro
    stop_grace_period: 2m
```

```powershell
# docker/setup-vm.ps1 - Run inside VM after first boot
# Installs everything needed for development

Set-ExecutionPolicy Bypass -Scope Process -Force

# Run the main installer
& C:\shared\install.ps1

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Blue
deskpilot status
deskpilot demo
```

---

## Verification

### Unit Tests
```bash
# Run from Windows or Docker VM
pytest tests/test_cua_bridge.py -v
```

### E2E Test (Calculator)
```bash
# Inside Windows VM or native Windows
deskpilot demo
# Should: Open Calculator, click 7, +, 8, =, verify result is 15
```

### SimCyp Test (manual)
```bash
deskpilot tui
> Open SimCyp and navigate to the Trial Design tab
```

---

## Implementation Order

1. **Create WinAppDriver client** (`winappdriver.py`)
   - REST API wrapper
   - Element finding and clicking

2. **Update WindowsComputer** (`computer.py`)
   - Replace NativeComputer
   - Integrate WinAppDriver with fallback

3. **Update configuration** (`config.py`, `default.yaml`)
   - Add windows.winappdriver section

4. **Update installer** (`install.ps1`, `windows.py`)
   - Download/install WinAppDriver
   - Enable Developer Mode

5. **Setup Docker environment** (`docker-compose.yml`, `setup-vm.ps1`)
   - Windows VM for development

6. **Write tests** (`test_winappdriver.py`)
   - Mock tests for client
   - E2E test with Calculator

---

## Dependencies

```toml
# pyproject.toml additions
dependencies = [
    # ... existing ...
    "aiohttp>=3.9.0",  # NEW: WinAppDriver REST client
]
```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| WinAppDriver not finding element | Fallback to pyautogui coordinates |
| WinAppDriver.exe crashes | Auto-restart on next operation |
| Slow element detection | Add caching for repeated clicks in same area |
| SimCyp doesn't support UI Automation | pyautogui fallback still works |
| Docker VM too slow without KVM | Acceptable for dev/test, prod runs native |

---

## Success Criteria

- [ ] Calculator demo works with WinAppDriver (not pyautogui)
- [ ] Fallback works when element not found
- [ ] `deskpilot install` sets up WinAppDriver automatically
- [ ] Docker VM boots and runs DeskPilot
- [ ] E2E test passes in both Docker and native Windows
