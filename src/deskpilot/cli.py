"""DeskPilot CLI - AI-powered desktop automation."""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from deskpilot import __version__

console = Console()


def async_command(f):
    """Decorator to run async click commands."""
    import functools

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.version_option(version=__version__, prog_name="deskpilot")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
@click.pass_context
def cli(ctx: click.Context, config: str | None) -> None:
    """DeskPilot - AI-powered desktop automation.

    Control desktop applications through natural language using local AI models.
    """
    ctx.ensure_object(dict)
    if config:
        from deskpilot.wizard.config import reload_config

        reload_config(config)


@cli.command()
@click.option("--skip-ollama", is_flag=True, help="Skip Ollama installation")
@click.option("--skip-openclaw", is_flag=True, help="Skip OpenClaw installation")
@click.option("--model", default="qwen2.5:3b", help="Ollama model to install")
@click.pass_context
def install(ctx: click.Context, skip_ollama: bool, skip_openclaw: bool, model: str) -> None:
    """Install DeskPilot and all dependencies.

    This command will:
    - Check system requirements
    - Install Ollama (if not present)
    - Pull the AI model
    - Install OpenClaw (if Node.js available)
    - Install the computer-use skill
    """
    from deskpilot.installer import NativeInstaller

    installer = NativeInstaller(
        skip_ollama=skip_ollama,
        skip_openclaw=skip_openclaw,
        model=model,
    )
    installer.run()


@cli.command()
@click.pass_context
def uninstall(ctx: click.Context) -> None:
    """Uninstall DeskPilot components.

    This removes:
    - The computer-use skill from OpenClaw
    - DeskPilot configuration files

    Note: Ollama and OpenClaw are NOT uninstalled as they may be used by other tools.
    """
    console.print("[blue]Uninstalling DeskPilot components...[/blue]")

    # Remove skill
    skill_path = Path.home() / ".openclaw" / "skills" / "computer-use"
    if skill_path.exists():
        import shutil

        shutil.rmtree(skill_path)
        console.print(f"  [green]Removed:[/green] {skill_path}")

    # Remove config
    config_path = Path("config/local.yaml")
    if config_path.exists():
        config_path.unlink()
        console.print(f"  [green]Removed:[/green] {config_path}")

    console.print()
    console.print("[green]DeskPilot uninstalled.[/green]")
    console.print("[dim]Note: Ollama and OpenClaw were not removed.[/dim]")


@cli.command()
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def demo(ctx: click.Context, mock: bool) -> None:
    """Run the interactive Calculator demo.

    This launches the OpenClaw TUI with a demo prompt to control Calculator.
    """
    from deskpilot.wizard.demo import run_calculator_demo

    await run_calculator_demo(mock=mock)


@cli.command()
@click.option("--save", "-s", is_flag=True, help="Save screenshot to disk")
@click.option("--describe", "-d", is_flag=True, help="Describe screen contents using AI")
@click.option("--output", "-o", type=click.Path(), help="Output path for screenshot")
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def screenshot(
    ctx: click.Context, save: bool, describe: bool, output: str | None, mock: bool
) -> None:
    """Capture a screenshot of the desktop.

    Examples:
        deskpilot screenshot --save
        deskpilot screenshot --describe
        deskpilot screenshot -s -o ./my_screenshot.png
    """
    from deskpilot.cua_bridge import create_actions

    actions = await create_actions(mock=mock)

    try:
        result = await actions.screenshot(save=save or (output is not None), describe=describe)

        if output:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            result.image.save(output)
            console.print(f"[green]Screenshot saved to:[/green] {output}")
        elif result.path:
            console.print(f"[green]Screenshot saved to:[/green] {result.path}")
        else:
            console.print("[green]Screenshot captured[/green]")
            screen_info = actions.computer.get_screen_info()
            console.print(f"Resolution: {screen_info.width}x{screen_info.height}")

        if result.description:
            console.print(Panel(result.description, title="Screen Description"))

    finally:
        await actions.computer.disconnect()


@cli.command("click")
@click.argument("x", type=int, required=False)
@click.argument("y", type=int, required=False)
@click.option("--target", "-t", type=str, help="Text/element to click on (requires AI)")
@click.option("--button", "-b", type=click.Choice(["left", "right", "middle"]), default="left")
@click.option("--double", is_flag=True, help="Double-click instead of single click")
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def click_cmd(
    ctx: click.Context,
    x: int | None,
    y: int | None,
    target: str | None,
    button: str,
    double: bool,
    mock: bool,
) -> None:
    """Click at coordinates or on a target element.

    Examples:
        deskpilot click 500 300
        deskpilot click 500 300 --button right
        deskpilot click --target "OK" (requires AI agent)
    """
    from deskpilot.cua_bridge import create_actions

    if x is None and y is None and target is None:
        console.print("[red]Error:[/red] Specify coordinates (x y) or --target")
        return

    actions = await create_actions(mock=mock)

    try:
        if double:
            if x is None or y is None:
                console.print("[red]Error:[/red] Double-click requires coordinates")
                return
            result = await actions.double_click(x, y)
        else:
            result = await actions.click(x=x, y=y, target=target, button=button)

        if result.success:
            console.print("[green]Click successful[/green]")
            if result.details:
                console.print(f"Details: {result.details}")
        else:
            console.print(f"[red]Click failed:[/red] {result.error}")

    finally:
        await actions.computer.disconnect()


@cli.command("type")
@click.argument("text")
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def type_cmd(ctx: click.Context, text: str, mock: bool) -> None:
    """Type text into the focused element.

    Examples:
        deskpilot type "Hello, World!"
        deskpilot type "user@example.com"
    """
    from deskpilot.cua_bridge import create_actions

    actions = await create_actions(mock=mock)

    try:
        result = await actions.type_text(text)

        if result.success:
            console.print(f"[green]Typed {len(text)} characters[/green]")
        else:
            console.print(f"[red]Type failed:[/red] {result.error}")

    finally:
        await actions.computer.disconnect()


@cli.command()
@click.argument("app")
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def launch(ctx: click.Context, app: str, mock: bool) -> None:
    """Launch an application by name.

    Uses the Start menu search on Windows, Spotlight on macOS.

    Examples:
        deskpilot launch Calculator
        deskpilot launch Notepad
        deskpilot launch "Microsoft Edge"
    """
    from deskpilot.cua_bridge import create_actions

    actions = await create_actions(mock=mock)

    try:
        console.print(f"[blue]Launching:[/blue] {app}")
        result = await actions.launch(app)

        if result.success:
            console.print("[green]Launched successfully[/green]")
        else:
            console.print(f"[red]Launch failed:[/red] {result.error}")

    finally:
        await actions.computer.disconnect()


@cli.command()
@click.argument("key")
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def press(ctx: click.Context, key: str, mock: bool) -> None:
    """Press a keyboard key.

    Examples:
        deskpilot press enter
        deskpilot press escape
        deskpilot press tab
    """
    from deskpilot.cua_bridge import create_actions

    actions = await create_actions(mock=mock)

    try:
        result = await actions.press_key(key)

        if result.success:
            console.print(f"[green]Pressed:[/green] {key}")
        else:
            console.print(f"[red]Press failed:[/red] {result.error}")

    finally:
        await actions.computer.disconnect()


@cli.command()
@click.argument("keys", nargs=-1, required=True)
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def hotkey(ctx: click.Context, keys: tuple, mock: bool) -> None:
    """Press a key combination.

    Examples:
        deskpilot hotkey ctrl c
        deskpilot hotkey ctrl shift escape
        deskpilot hotkey alt f4
    """
    from deskpilot.cua_bridge import create_actions

    actions = await create_actions(mock=mock)

    try:
        result = await actions.hotkey(*keys)

        if result.success:
            console.print(f"[green]Pressed:[/green] {' + '.join(keys)}")
        else:
            console.print(f"[red]Hotkey failed:[/red] {result.error}")

    finally:
        await actions.computer.disconnect()


@cli.command()
@click.argument("task")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed reasoning")
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def run(ctx: click.Context, task: str, verbose: bool, mock: bool) -> None:
    """Run an AI-controlled task.

    The AI agent will analyze the screen and perform actions to complete the task.

    Examples:
        deskpilot run "Open Calculator and compute 15 * 8"
        deskpilot run "Find and click the Settings button"
    """
    from deskpilot.cua_bridge import create_agent

    console.print(f"[blue]Task:[/blue] {task}")
    console.print()

    agent = await create_agent(mock=mock)

    try:
        result = await agent.execute(task, verbose=verbose)

        console.print()
        if result.success:
            console.print(f"[green]Task completed in {result.total_steps} steps[/green]")
            if result.final_answer:
                console.print(Panel(result.final_answer, title="Result"))
        else:
            console.print(f"[red]Task failed:[/red] {result.error}")

    finally:
        await agent.computer.disconnect()


@cli.command()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Show current configuration."""
    from deskpilot.wizard.config import find_config_file, get_config

    cfg = get_config()
    config_file = find_config_file()

    table = Table(title="DeskPilot Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Config File", str(config_file) if config_file else "None (using defaults)")
    table.add_row("Model Provider", cfg.model.provider)
    table.add_row("Model Name", cfg.model.name)
    table.add_row("Model Base URL", cfg.model.base_url)
    table.add_row("Agent Max Steps", str(cfg.agent.max_steps))
    table.add_row("OpenClaw Enabled", str(cfg.openclaw.enabled))
    table.add_row("OpenClaw TUI Auto-Start", str(cfg.openclaw.auto_start_tui))
    table.add_row("Log Level", cfg.logging.level)

    console.print(table)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Check the status of DeskPilot dependencies."""
    from deskpilot.wizard.setup import check_dependencies

    asyncio.run(check_dependencies())


@cli.command()
@click.pass_context
def tui(ctx: click.Context) -> None:
    """Launch the OpenClaw TUI (interactive mode).

    This opens the OpenClaw dashboard where you can interact with DeskPilot
    using natural language.
    """
    if not shutil.which("openclaw"):
        console.print("[red]Error:[/red] OpenClaw not installed")
        console.print("Install with: npm install -g openclaw@latest")
        return

    console.print("[blue]Launching OpenClaw TUI...[/blue]")
    subprocess.run(["openclaw", "dashboard"])


if __name__ == "__main__":
    cli()
