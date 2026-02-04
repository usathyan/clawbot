"""Calculator demo for DeskPilot."""

from __future__ import annotations

import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from deskpilot.cua_bridge import create_actions, create_agent
from deskpilot.wizard.config import get_config

console = Console()


async def run_calculator_demo(mock: bool = False) -> None:
    """Run the interactive Calculator demo.

    Args:
        mock: If True, use mock mode for testing.
    """
    console.print(
        Panel(
            "[bold blue]DeskPilot Calculator Demo[/bold blue]\n\n"
            "This demo shows AI-controlled Windows automation.\n"
            "The agent will launch Calculator and perform calculations.",
            expand=False,
        )
    )
    console.print()

    config = get_config()
    console.print(f"[dim]Mode: {config.deployment.mode}[/dim]")
    console.print(f"[dim]Model: {config.model.provider}/{config.model.name}[/dim]")
    console.print()

    # Initialize
    console.print("[bold]Initializing...[/bold]")
    agent = await create_agent(mock=mock)
    actions = await create_actions(mock=mock)

    try:
        # Step 1: Launch Calculator
        console.print()
        console.print("[bold cyan]Step 1: Launching Calculator[/bold cyan]")

        result = await actions.launch("Calculator")
        if not result.success:
            console.print(f"[red]Failed to launch Calculator:[/red] {result.error}")
            return

        await asyncio.sleep(1.5)  # Wait for app to start
        console.print("[green]Calculator launched[/green]")

        # Take initial screenshot
        screenshot = await actions.screenshot(save=True)
        if screenshot.path:
            console.print(f"[dim]Screenshot saved: {screenshot.path}[/dim]")

        # Interactive loop
        console.print()
        console.print("[bold cyan]Step 2: Interactive Mode[/bold cyan]")
        console.print("Enter calculations (e.g., '2 + 2', '15 * 8', '100 / 4')")
        console.print("Type 'quit' to exit")
        console.print()

        while True:
            try:
                user_input = Prompt.ask("[bold]Calculate[/bold]")
            except (KeyboardInterrupt, EOFError):
                break

            if user_input.lower() in ("quit", "exit", "q"):
                break

            if not user_input.strip():
                continue

            # Build task for the agent
            task = f"Use the Calculator to compute: {user_input}. Click the buttons to enter the calculation, then tell me the result."

            console.print()
            console.print(f"[blue]Task:[/blue] {task}")
            console.print()

            # Run the agent
            result = await agent.execute(task, verbose=True)

            console.print()
            if result.success:
                console.print(f"[green]Completed in {result.total_steps} steps[/green]")
                if result.final_answer:
                    console.print(
                        Panel(
                            f"[bold]{user_input}[/bold] = [green]{result.final_answer}[/green]",
                            title="Result",
                            expand=False,
                        )
                    )
            else:
                console.print(f"[red]Failed:[/red] {result.error}")

            console.print()

        # Cleanup
        console.print()
        console.print("[bold cyan]Closing Calculator...[/bold cyan]")
        await actions.hotkey("alt", "f4")
        console.print("[green]Demo complete![/green]")

    finally:
        await agent.computer.disconnect()
        await actions.computer.disconnect()


async def run_quick_demo(mock: bool = False) -> None:
    """Run a quick non-interactive demo.

    Args:
        mock: If True, use mock mode for testing.
    """
    console.print("[bold]Quick Calculator Demo[/bold]")
    console.print()

    agent = await create_agent(mock=mock)

    try:
        # Run a single calculation
        task = "Open Calculator, compute 2 + 2, and tell me the result"
        console.print(f"[blue]Task:[/blue] {task}")
        console.print()

        result = await agent.execute(task, verbose=True)

        console.print()
        if result.success:
            console.print(
                Panel(
                    f"Result: {result.final_answer or 'Calculation complete'}",
                    title="Demo Complete",
                    border_style="green",
                )
            )
        else:
            console.print(f"[red]Demo failed:[/red] {result.error}")

    finally:
        await agent.computer.disconnect()
