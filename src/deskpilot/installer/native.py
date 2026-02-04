"""Native installer for DeskPilot."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


@dataclass
class InstallResult:
    """Result of an installation step."""

    success: bool
    message: str
    details: str | None = None


class NativeInstaller:
    """Install DeskPilot and dependencies on the native system."""

    def __init__(
        self,
        skip_ollama: bool = False,
        skip_openclaw: bool = False,
        model: str = "qwen2.5:3b",
    ):
        self.skip_ollama = skip_ollama
        self.skip_openclaw = skip_openclaw
        self.model = model
        self.system = platform.system()
        self.arch = platform.machine()

    def check_python(self) -> InstallResult:
        """Check Python version meets requirements."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 11:
            return InstallResult(
                success=True,
                message=f"Python {version.major}.{version.minor} found",
            )
        return InstallResult(
            success=False,
            message=f"Python 3.11+ required (found {version.major}.{version.minor})",
        )

    def check_ollama(self) -> InstallResult:
        """Check if Ollama is installed."""
        if shutil.which("ollama"):
            return InstallResult(success=True, message="Ollama found")
        return InstallResult(success=False, message="Ollama not found")

    def install_ollama(self) -> InstallResult:
        """Install Ollama."""
        console.print("[blue]Installing Ollama...[/blue]")

        try:
            if self.system == "Darwin":
                # macOS - try brew first
                if shutil.which("brew"):
                    subprocess.run(["brew", "install", "ollama"], check=True)
                else:
                    subprocess.run(
                        ["sh", "-c", "curl -fsSL https://ollama.ai/install.sh | sh"],
                        check=True,
                    )
            elif self.system == "Linux":
                subprocess.run(
                    ["sh", "-c", "curl -fsSL https://ollama.ai/install.sh | sh"],
                    check=True,
                )
            elif self.system == "Windows":
                console.print(
                    "[yellow]Please download Ollama from https://ollama.ai/download[/yellow]"
                )
                return InstallResult(
                    success=False,
                    message="Manual installation required on Windows",
                )
            else:
                return InstallResult(
                    success=False,
                    message=f"Unsupported OS: {self.system}",
                )

            return InstallResult(success=True, message="Ollama installed")
        except subprocess.CalledProcessError as e:
            return InstallResult(
                success=False,
                message="Failed to install Ollama",
                details=str(e),
            )

    def start_ollama_service(self) -> InstallResult:
        """Start Ollama service if not running."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                return InstallResult(success=True, message="Ollama service running")

            # Try to start the service
            if self.system == "Darwin" or self.system == "Linux":
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return InstallResult(success=True, message="Ollama service started")
        except Exception as e:
            return InstallResult(
                success=False,
                message="Could not start Ollama service",
                details=str(e),
            )

    def pull_model(self) -> InstallResult:
        """Pull the AI model."""
        console.print(f"[blue]Pulling model {self.model}...[/blue]")

        try:
            subprocess.run(["ollama", "pull", self.model], check=True)
            return InstallResult(
                success=True,
                message=f"Model {self.model} ready",
            )
        except subprocess.CalledProcessError as e:
            return InstallResult(
                success=False,
                message=f"Failed to pull model {self.model}",
                details=str(e),
            )

    def check_node(self) -> InstallResult:
        """Check if Node.js is installed."""
        if not shutil.which("node"):
            return InstallResult(success=False, message="Node.js not found")

        try:
            result = subprocess.run(
                ["node", "-v"],
                capture_output=True,
                text=True,
            )
            version = result.stdout.strip().lstrip("v")
            major = int(version.split(".")[0])
            if major >= 18:
                return InstallResult(
                    success=True,
                    message=f"Node.js v{major} found",
                )
            return InstallResult(
                success=False,
                message=f"Node.js 18+ required (found v{major})",
            )
        except Exception as e:
            return InstallResult(
                success=False,
                message="Could not check Node.js version",
                details=str(e),
            )

    def install_openclaw(self) -> InstallResult:
        """Install OpenClaw globally via npm."""
        console.print("[blue]Installing OpenClaw...[/blue]")

        try:
            subprocess.run(
                ["npm", "install", "-g", "openclaw@latest"],
                check=True,
            )
            return InstallResult(success=True, message="OpenClaw installed")
        except subprocess.CalledProcessError as e:
            return InstallResult(
                success=False,
                message="Failed to install OpenClaw",
                details=str(e),
            )

    def install_skill(self) -> InstallResult:
        """Install the computer-use skill to OpenClaw directory."""
        console.print("[blue]Installing computer-use skill...[/blue]")

        # Find skill source
        skill_src = Path(__file__).parent.parent / "openclaw_skill" / "computer-use"
        skill_dest = Path.home() / ".openclaw" / "skills" / "computer-use"

        if not skill_src.exists():
            return InstallResult(
                success=False,
                message="Skill source not found",
                details=str(skill_src),
            )

        try:
            skill_dest.parent.mkdir(parents=True, exist_ok=True)
            if skill_dest.exists():
                shutil.rmtree(skill_dest)
            shutil.copytree(skill_src, skill_dest)
            return InstallResult(
                success=True,
                message=f"Skill installed to {skill_dest}",
            )
        except Exception as e:
            return InstallResult(
                success=False,
                message="Failed to install skill",
                details=str(e),
            )

    def smoke_test(self) -> InstallResult:
        """Run a smoke test to verify installation."""
        console.print("[blue]Running smoke test...[/blue]")

        errors = []

        # Check deskpilot CLI
        if shutil.which("deskpilot"):
            try:
                result = subprocess.run(
                    ["deskpilot", "--version"],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    errors.append("deskpilot --version failed")
            except Exception as e:
                errors.append(f"deskpilot: {e}")
        else:
            errors.append("deskpilot not in PATH")

        # Check Ollama
        if not self.skip_ollama:
            try:
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    errors.append("ollama list failed")
            except Exception as e:
                errors.append(f"ollama: {e}")

        if errors:
            return InstallResult(
                success=False,
                message="Some checks failed",
                details="\n".join(errors),
            )
        return InstallResult(success=True, message="All checks passed")

    def run(self) -> bool:
        """Run the full installation process."""
        console.print(
            Panel(
                "[bold blue]DeskPilot Installer[/bold blue]\n"
                "AI-Powered Desktop Automation",
                expand=False,
            )
        )

        console.print(f"\n[blue]System:[/blue] {self.system} ({self.arch})\n")

        steps = []

        # Check Python
        result = self.check_python()
        steps.append(("Python", result))
        if not result.success:
            console.print(f"[red]Error:[/red] {result.message}")
            return False

        # Install Ollama
        if not self.skip_ollama:
            result = self.check_ollama()
            if not result.success:
                result = self.install_ollama()
            steps.append(("Ollama", result))

            if result.success:
                self.start_ollama_service()
                result = self.pull_model()
                steps.append(("AI Model", result))

        # Install OpenClaw
        if not self.skip_openclaw:
            result = self.check_node()
            if result.success:
                result = self.install_openclaw()
                steps.append(("OpenClaw", result))
            else:
                console.print(
                    "[yellow]Skipping OpenClaw (Node.js 18+ required)[/yellow]"
                )

        # Install skill
        result = self.install_skill()
        steps.append(("Skill", result))

        # Show results
        console.print("\n[bold]Installation Summary:[/bold]\n")
        for name, result in steps:
            status = "[green]OK[/green]" if result.success else "[red]FAIL[/red]"
            console.print(f"  {status} {name}: {result.message}")

        # Smoke test
        console.print()
        result = self.smoke_test()

        console.print(
            Panel(
                "[bold green]Installation Complete![/bold green]\n\n"
                "Next steps:\n"
                "  1. Start Ollama: [cyan]ollama serve[/cyan]\n"
                "  2. Launch TUI:   [cyan]openclaw dashboard[/cyan]\n"
                "  3. Or run demo:  [cyan]deskpilot demo[/cyan]",
                expand=False,
            )
        )

        return True
