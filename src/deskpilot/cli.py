"""DeskPilot CLI - AI-powered Windows automation."""

from __future__ import annotations

import asyncio
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
    """DeskPilot - AI-powered Windows automation with OpenClaw + Cua.

    Control Windows applications through natural language using local AI models.
    """
    ctx.ensure_object(dict)
    if config:
        from deskpilot.wizard.config import reload_config

        reload_config(config)


@cli.command()
@click.pass_context
@async_command
async def setup(ctx: click.Context) -> None:
    """Run the interactive setup wizard.

    Guides you through configuring DeskPilot for your environment.
    """
    from deskpilot.wizard.setup import run_setup_wizard

    await run_setup_wizard()


@cli.command()
@click.option("--mock", is_flag=True, help="Use mock mode for testing")
@click.pass_context
@async_command
async def demo(ctx: click.Context, mock: bool) -> None:
    """Run the Calculator demo.

    Demonstrates AI-controlled automation with the Windows Calculator.
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
    """Capture a screenshot of the controlled computer.

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

    Uses the Start menu search on Windows.

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
    table.add_row("Deployment Mode", cfg.deployment.mode)
    table.add_row("Model Provider", cfg.model.provider)
    table.add_row("Model Name", cfg.model.name)
    table.add_row("Model Base URL", cfg.model.base_url)
    table.add_row("Agent Max Steps", str(cfg.agent.max_steps))
    table.add_row("OpenClaw Enabled", str(cfg.openclaw.enabled))
    table.add_row("Log Level", cfg.logging.level)

    if cfg.deployment.mode == "vm":
        table.add_row("VM OS Type", cfg.vm.os_type)
        table.add_row("VM Provider", cfg.vm.provider_type)
        table.add_row("VM Display", cfg.vm.display)
        table.add_row("VM RAM", cfg.vm.ram_size)
        table.add_row("VM CPUs", str(cfg.vm.cpu_cores))

    console.print(table)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Check the status of DeskPilot dependencies."""
    from deskpilot.wizard.setup import check_dependencies

    asyncio.run(check_dependencies())


if __name__ == "__main__":
    cli()
