"""WinAppDriver installer for Windows."""

from __future__ import annotations

import logging
import platform
import subprocess
import urllib.request
from pathlib import Path

from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

WINAPPDRIVER_URL = (
    "https://github.com/microsoft/WinAppDriver/releases/download/"
    "v1.2.1/WindowsApplicationDriver_1.2.1.msi"
)
WINAPPDRIVER_PATH = Path(
    r"C:\Program Files\Windows Application Driver\WinAppDriver.exe"
)


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


def is_winappdriver_installed() -> bool:
    """Check if WinAppDriver is installed."""
    return WINAPPDRIVER_PATH.exists()


def is_developer_mode_enabled() -> bool:
    """Check if Windows Developer Mode is enabled (required for WinAppDriver)."""
    if not is_windows():
        return False

    try:
        result = subprocess.run(
            [
                "reg",
                "query",
                r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock",
                "/v",
                "AllowDevelopmentWithoutDevLicense",
            ],
            capture_output=True,
            text=True,
        )
        return "0x1" in result.stdout
    except Exception:
        return False


def install_winappdriver() -> bool:
    """Download and install WinAppDriver.

    Returns True if installation succeeded.
    """
    if not is_windows():
        console.print("[yellow]WinAppDriver is Windows-only. Skipping.[/yellow]")
        return False

    if is_winappdriver_installed():
        console.print("[green]  WinAppDriver already installed[/green]")
        return True

    console.print("[blue]  Downloading WinAppDriver...[/blue]")

    try:
        installer_path = Path.home() / "Downloads" / "WinAppDriver.msi"
        urllib.request.urlretrieve(WINAPPDRIVER_URL, str(installer_path))

        console.print("[blue]  Running installer (requires admin)...[/blue]")
        subprocess.run(
            ["msiexec", "/i", str(installer_path), "/quiet", "/norestart"],
            check=True,
        )

        installer_path.unlink(missing_ok=True)

        if is_winappdriver_installed():
            console.print("[green]  WinAppDriver installed[/green]")
            return True
        else:
            console.print("[red]  WinAppDriver installation may have failed[/red]")
            return False

    except Exception as e:
        console.print(f"[red]  WinAppDriver installation failed: {e}[/red]")
        return False


def enable_developer_mode() -> bool:
    """Enable Windows Developer Mode (required for WinAppDriver).

    Returns True if Developer Mode is enabled.
    """
    if not is_windows():
        return False

    if is_developer_mode_enabled():
        console.print("[green]  Developer Mode already enabled[/green]")
        return True

    console.print("[blue]  Enabling Developer Mode (requires admin)...[/blue]")

    try:
        subprocess.run(
            [
                "reg",
                "add",
                r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock",
                "/v",
                "AllowDevelopmentWithoutDevLicense",
                "/t",
                "REG_DWORD",
                "/d",
                "1",
                "/f",
            ],
            check=True,
            capture_output=True,
        )
        console.print("[green]  Developer Mode enabled[/green]")
        return True
    except subprocess.CalledProcessError:
        console.print(
            "[yellow]  Could not enable Developer Mode. "
            "Run as Administrator or enable manually in Settings.[/yellow]"
        )
        return False
