"""Interactive setup wizard for DeskPilot."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from deskpilot.wizard.config import DeskPilotConfig, save_config

console = Console()


async def check_dependencies() -> dict[str, bool]:
    """Check which dependencies are available.

    Returns:
        Dict mapping dependency name to availability.
    """
    results = {}

    # Check Python version
    py_version = platform.python_version_tuple()
    results["python_3.12+"] = int(py_version[0]) >= 3 and int(py_version[1]) >= 12

    # Check Docker
    results["docker"] = shutil.which("docker") is not None

    # Check Ollama
    results["ollama"] = shutil.which("ollama") is not None

    # Check for cua-agent package
    try:
        import computer  # noqa: F401

        results["cua-agent"] = True
    except ImportError:
        results["cua-agent"] = False

    # Check for native packages
    try:
        import mss  # noqa: F401
        import pyautogui  # noqa: F401

        results["native-packages"] = True
    except ImportError:
        results["native-packages"] = False

    # Check OpenClaw (optional)
    results["openclaw"] = shutil.which("openclaw") is not None

    # Check system
    results["is_windows"] = platform.system() == "Windows"
    results["is_macos"] = platform.system() == "Darwin"
    results["is_linux"] = platform.system() == "Linux"

    # Print status table
    table = Table(title="Dependency Status")
    table.add_column("Dependency", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Notes", style="dim")

    def status_str(available: bool) -> str:
        return "[green]Available[/green]" if available else "[red]Missing[/red]"

    table.add_row(
        "Python 3.12+",
        status_str(results["python_3.12+"]),
        f"Current: {platform.python_version()}",
    )
    table.add_row(
        "Docker",
        status_str(results["docker"]),
        "Required for VM mode",
    )
    table.add_row(
        "Ollama",
        status_str(results["ollama"]),
        "Local AI inference",
    )
    table.add_row(
        "cua-agent",
        status_str(results["cua-agent"]),
        "Cua SDK",
    )
    table.add_row(
        "Native packages",
        status_str(results["native-packages"]),
        "pyautogui + mss (optional)",
    )
    table.add_row(
        "OpenClaw",
        status_str(results["openclaw"]),
        "Optional integration",
    )

    console.print(table)
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


async def pull_ollama_model(model: str) -> bool:
    """Pull an Ollama model.

    Args:
        model: Model name to pull.

    Returns:
        True if successful.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Pulling {model}...", total=None)

        try:
            result = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True,
                text=True,
            )
            progress.update(task, completed=True)

            if result.returncode == 0:
                console.print(f"[green]Model {model} ready[/green]")
                return True
            else:
                console.print(f"[red]Failed to pull model:[/red] {result.stderr}")
                return False
        except Exception as e:
            console.print(f"[red]Error pulling model:[/red] {e}")
            return False


def install_openclaw_skill() -> bool:
    """Install the computer-use skill to OpenClaw.

    Returns:
        True if successful.
    """
    skill_source = Path(__file__).parent.parent / "openclaw_skill" / "computer-use"
    skill_dest = Path.home() / ".openclaw" / "skills" / "computer-use"

    try:
        if skill_source.exists():
            skill_dest.parent.mkdir(parents=True, exist_ok=True)
            if skill_dest.exists():
                shutil.rmtree(skill_dest)
            shutil.copytree(skill_source, skill_dest)
            console.print(f"[green]Installed skill to:[/green] {skill_dest}")
            return True
        else:
            console.print("[yellow]Skill source not found, skipping installation[/yellow]")
            return False
    except Exception as e:
        console.print(f"[red]Failed to install skill:[/red] {e}")
        return False


async def run_setup_wizard() -> None:
    """Run the interactive setup wizard."""
    console.print(
        Panel(
            "[bold blue]DeskPilot Setup Wizard[/bold blue]\n\n"
            "This wizard will help you configure DeskPilot for your environment.",
            expand=False,
        )
    )
    console.print()

    # Detect environment
    console.print("[bold]Detecting environment...[/bold]")
    env = detect_environment()
    console.print(f"  OS: {env['os']} ({env['arch']})")
    console.print(f"  Python: {env['python_version']}")
    console.print(f"  RAM: ~{env['ram_gb']}GB")
    console.print()

    # Check dependencies
    console.print("[bold]Checking dependencies...[/bold]")
    deps = await check_dependencies()
    console.print()

    # Choose deployment mode
    console.print("[bold]Deployment Mode[/bold]")
    console.print("  [cyan]vm[/cyan]: Run Windows in a Docker VM (safe sandbox)")
    console.print("  [cyan]native[/cyan]: Control local Windows directly")
    console.print()

    if env["os"] == "Windows":
        default_mode = "native"
        console.print("[dim]Detected Windows - defaulting to native mode[/dim]")
    elif deps["docker"]:
        default_mode = "vm"
        console.print("[dim]Docker available - defaulting to VM mode[/dim]")
    else:
        default_mode = "native"
        console.print("[yellow]Docker not found - defaulting to native mode[/yellow]")

    mode = Prompt.ask(
        "Deployment mode",
        choices=["vm", "native"],
        default=default_mode,
    )

    # Create config
    config = DeskPilotConfig()
    config.deployment.mode = mode

    # VM-specific setup
    if mode == "vm":
        if not deps["docker"]:
            console.print(
                "[red]Error:[/red] Docker is required for VM mode. "
                "Please install Docker and try again."
            )
            return

        console.print()
        console.print("[bold]VM Configuration[/bold]")

        # RAM
        default_ram = "8G" if env["ram_gb"] >= 16 else "4G"
        ram = Prompt.ask("VM RAM allocation", default=default_ram)
        config.vm.ram_size = ram

        # CPUs
        cpu_count = os.cpu_count() or 4
        default_cpus = min(4, cpu_count - 2)
        cpus = Prompt.ask("VM CPU cores", default=str(default_cpus))
        config.vm.cpu_cores = int(cpus)

    # Native-specific setup
    if mode == "native":
        if not deps["native-packages"]:
            console.print()
            install = Confirm.ask(
                "Native packages (pyautogui, mss) not found. Install them?",
                default=True,
            )
            if install:
                subprocess.run(
                    ["uv", "pip", "install", "pyautogui", "mss", "pillow"],
                    check=True,
                )
                console.print("[green]Packages installed[/green]")

    # Model setup
    console.print()
    console.print("[bold]AI Model Configuration[/bold]")

    if deps["ollama"]:
        model = Prompt.ask(
            "Ollama model",
            default="qwen2.5:3b",
        )
        config.model.name = model

        pull = Confirm.ask(f"Pull model '{model}' now?", default=True)
        if pull:
            await pull_ollama_model(model)
    else:
        console.print(
            "[yellow]Ollama not found.[/yellow] "
            "Install from https://ollama.ai and run 'ollama pull qwen2.5:3b'"
        )

    # OpenClaw integration
    console.print()
    if deps["openclaw"]:
        enable_openclaw = Confirm.ask(
            "Enable OpenClaw integration?",
            default=True,
        )
        config.openclaw.enabled = enable_openclaw

        if enable_openclaw:
            install_skill = Confirm.ask("Install computer-use skill?", default=True)
            if install_skill:
                install_openclaw_skill()
    else:
        console.print(
            "[dim]OpenClaw not found. Install with: npm install -g openclaw@latest[/dim]"
        )

    # Save configuration
    console.print()
    config_path = Path("config/local.yaml")
    save_config(config, config_path)
    console.print(f"[green]Configuration saved to:[/green] {config_path}")

    # Summary
    console.print()
    console.print(
        Panel(
            f"[bold green]Setup Complete![/bold green]\n\n"
            f"Mode: {mode}\n"
            f"Model: {config.model.provider}/{config.model.name}\n\n"
            f"Next steps:\n"
            f"  1. {'Start VM: make vm-up' if mode == 'vm' else 'Ensure Windows is running'}\n"
            f"  2. Run demo: deskpilot demo\n"
            f"  3. Or try: deskpilot run 'Open Calculator'",
            expand=False,
        )
    )
