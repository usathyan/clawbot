"""Dependency checking and status utilities for DeskPilot."""

from __future__ import annotations

import platform
import shutil
import subprocess

from rich.console import Console
from rich.table import Table

console = Console()


async def check_dependencies() -> dict[str, bool]:
    """Check which dependencies are available.

    Returns:
        Dict mapping dependency name to availability.
    """
    results = {}

    # Check Python version
    py_version = platform.python_version_tuple()
    results["python_3.11+"] = int(py_version[0]) >= 3 and int(py_version[1]) >= 11

    # Check Ollama
    results["ollama"] = shutil.which("ollama") is not None

    # Check if Ollama is running
    if results["ollama"]:
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                timeout=5,
            )
            results["ollama_running"] = result.returncode == 0
        except Exception:
            results["ollama_running"] = False
    else:
        results["ollama_running"] = False

    # Check for native packages
    try:
        import mss  # noqa: F401
        import pyautogui  # noqa: F401

        results["native-packages"] = True
    except ImportError:
        results["native-packages"] = False

    # Check OpenClaw
    results["openclaw"] = shutil.which("openclaw") is not None

    # Check Node.js
    if shutil.which("node"):
        try:
            result = subprocess.run(
                ["node", "-v"],
                capture_output=True,
                text=True,
            )
            version = result.stdout.strip().lstrip("v")
            major = int(version.split(".")[0])
            results["node_18+"] = major >= 18
        except Exception:
            results["node_18+"] = False
    else:
        results["node_18+"] = False

    # Check system
    results["is_windows"] = platform.system() == "Windows"
    results["is_macos"] = platform.system() == "Darwin"
    results["is_linux"] = platform.system() == "Linux"

    # Print status table
    table = Table(title="DeskPilot Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Notes", style="dim")

    def status_str(available: bool) -> str:
        return "[green]OK[/green]" if available else "[red]Missing[/red]"

    table.add_row(
        "Python 3.11+",
        status_str(results["python_3.11+"]),
        f"Current: {platform.python_version()}",
    )
    table.add_row(
        "Ollama",
        status_str(results["ollama"]),
        "Local AI inference",
    )
    table.add_row(
        "Ollama Service",
        status_str(results["ollama_running"]),
        "Run: ollama serve",
    )
    table.add_row(
        "Native packages",
        status_str(results["native-packages"]),
        "pyautogui + mss + pillow",
    )
    table.add_row(
        "Node.js 18+",
        status_str(results["node_18+"]),
        "Required for OpenClaw",
    )
    table.add_row(
        "OpenClaw",
        status_str(results["openclaw"]),
        "TUI interface",
    )

    console.print(table)

    # Show recommendations
    console.print()
    if not results["ollama"]:
        console.print("[yellow]Install Ollama:[/yellow] https://ollama.ai")
    elif not results["ollama_running"]:
        console.print("[yellow]Start Ollama:[/yellow] ollama serve")

    if not results["native-packages"]:
        console.print(
            "[yellow]Install native packages:[/yellow] pip install pyautogui mss pillow"
        )

    if not results["openclaw"]:
        if results["node_18+"]:
            console.print("[yellow]Install OpenClaw:[/yellow] npm install -g openclaw@latest")
        else:
            console.print("[yellow]Install Node.js 18+:[/yellow] https://nodejs.org")

    return results


def detect_environment() -> dict:
    """Detect the current environment.

    Returns:
        Dict with environment details.
    """
    env = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "arch": platform.machine(),
    }

    # Check RAM (approximate)
    try:
        if platform.system() == "Darwin":
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
            )
            env["ram_gb"] = int(result.stdout.strip()) // (1024**3)
        elif platform.system() == "Linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        env["ram_gb"] = kb // (1024**2)
                        break
        else:
            env["ram_gb"] = 8  # Default assumption
    except Exception:
        env["ram_gb"] = 8

    return env
