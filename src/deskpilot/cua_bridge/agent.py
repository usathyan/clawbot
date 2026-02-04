"""AI Agent wrapper for computer automation."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from deskpilot.cua_bridge.computer import BaseComputer, get_computer
from deskpilot.wizard.config import DeskPilotConfig, get_config

if TYPE_CHECKING:
    from PIL import Image

console = Console()


@dataclass
class AgentStep:
    """A single step in the agent's execution."""

    step_number: int
    reasoning: str | None = None
    action: str | None = None
    action_params: dict | None = None
    screenshot: Image.Image | None = None
    result: Any = None
    error: str | None = None


@dataclass
class AgentResult:
    """Result of an agent task execution."""

    success: bool
    task: str
    steps: list[AgentStep] = field(default_factory=list)
    final_answer: str | None = None
    error: str | None = None

    @property
    def total_steps(self) -> int:
        return len(self.steps)


class DeskPilotAgent:
    """AI Agent that can see and control computers.

    Uses Cua's ComputerAgent with Ollama for local inference.
    """

    def __init__(
        self,
        computer: BaseComputer,
        config: DeskPilotConfig | None = None,
    ) -> None:
        self.computer = computer
        self.config = config or get_config()
        self._agent = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the Cua ComputerAgent."""
        if self._initialized:
            return

        try:
            from agent import ComputerAgent
        except ImportError as e:
            raise ImportError(
                "cua-agent package not installed. Run: uv pip install cua-agent"
            ) from e

        # Build model string for liteLLM
        model_config = self.config.model
        if model_config.provider == "ollama":
            model_str = f"ollama/{model_config.name}"
        else:
            model_str = model_config.name

        # Create ComputerAgent with our computer instance
        self._agent = ComputerAgent(
            model=model_str,
            computer=self.computer._computer if hasattr(self.computer, "_computer") else None,
        )
        self._initialized = True

    async def run(
        self,
        task: str,
        verbose: bool | None = None,
    ) -> AsyncIterator[AgentStep]:
        """Run a task and yield steps as they complete.

        Args:
            task: Natural language task description.
            verbose: Print steps to console. If None, uses config.

        Yields:
            AgentStep for each action taken.
        """
        if verbose is None:
            verbose = self.config.agent.verbose

        if not self._initialized:
            await self.initialize()

        if not self._agent:
            raise RuntimeError("Agent not initialized")

        step_num = 0
        messages = [{"role": "user", "content": task}]

        try:
            async for result in self._agent.run(messages):
                step_num += 1
                step = AgentStep(step_number=step_num)

                # Parse result based on Cua's output format
                if isinstance(result, dict):
                    step.reasoning = result.get("reasoning")
                    step.action = result.get("action")
                    step.action_params = result.get("params")
                    step.result = result.get("result")
                    step.error = result.get("error")
                else:
                    step.result = result

                # Capture screenshot after action if configured
                if self.config.agent.screenshot_on_step:
                    try:
                        step.screenshot = await self.computer.screenshot()
                    except Exception:
                        pass  # Don't fail on screenshot errors

                if verbose:
                    self._print_step(step)

                yield step

                # Check step limit
                if step_num >= self.config.agent.max_steps:
                    break

        except Exception as e:
            error_step = AgentStep(
                step_number=step_num + 1,
                error=str(e),
            )
            if verbose:
                self._print_step(error_step)
            yield error_step

    async def execute(self, task: str, verbose: bool | None = None) -> AgentResult:
        """Execute a task and return the complete result.

        Args:
            task: Natural language task description.
            verbose: Print steps to console.

        Returns:
            AgentResult with all steps and final answer.
        """
        steps = []
        last_error = None

        async for step in self.run(task, verbose=verbose):
            steps.append(step)
            if step.error:
                last_error = step.error

        # Determine success and extract final answer
        success = last_error is None and len(steps) > 0
        final_answer = None

        if steps:
            last_step = steps[-1]
            if last_step.result:
                final_answer = str(last_step.result)

        return AgentResult(
            success=success,
            task=task,
            steps=steps,
            final_answer=final_answer,
            error=last_error,
        )

    def _print_step(self, step: AgentStep) -> None:
        """Print a step to the console."""
        title = f"Step {step.step_number}"

        if step.error:
            content = Text(f"Error: {step.error}", style="red")
            console.print(Panel(content, title=title, border_style="red"))
            return

        lines = []

        if step.reasoning:
            lines.append(f"[bold]Reasoning:[/bold] {step.reasoning}")

        if step.action:
            action_str = step.action
            if step.action_params:
                params_str = ", ".join(f"{k}={v}" for k, v in step.action_params.items())
                action_str = f"{step.action}({params_str})"
            lines.append(f"[bold]Action:[/bold] {action_str}")

        if step.result:
            lines.append(f"[bold]Result:[/bold] {step.result}")

        content = "\n".join(lines) if lines else "Processing..."
        console.print(Panel(content, title=title, border_style="blue"))


class MockAgent:
    """Mock agent for testing without AI backend."""

    def __init__(self, computer: BaseComputer, config: DeskPilotConfig | None = None) -> None:
        self.computer = computer
        self.config = config or get_config()
        self._initialized = True

    async def initialize(self) -> None:
        pass

    async def run(self, task: str, verbose: bool | None = None) -> AsyncIterator[AgentStep]:
        """Simulate agent execution for testing."""
        # Simulate a few steps
        steps = [
            AgentStep(
                step_number=1,
                reasoning=f"I need to {task}",
                action="screenshot",
                result="Captured screen",
            ),
            AgentStep(
                step_number=2,
                reasoning="Analyzing the screen",
                action="click",
                action_params={"x": 100, "y": 100},
                result="Clicked successfully",
            ),
            AgentStep(
                step_number=3,
                reasoning="Task appears complete",
                result=f"Completed: {task}",
            ),
        ]

        for step in steps:
            if verbose:
                self._print_step(step)
            yield step
            await asyncio.sleep(0.1)  # Simulate processing time

    async def execute(self, task: str, verbose: bool | None = None) -> AgentResult:
        steps = [step async for step in self.run(task, verbose=verbose)]
        return AgentResult(
            success=True,
            task=task,
            steps=steps,
            final_answer=f"Completed: {task}",
        )

    def _print_step(self, step: AgentStep) -> None:
        DeskPilotAgent._print_step(self, step)


async def create_agent(mock: bool = False) -> DeskPilotAgent | MockAgent:
    """Create and initialize an agent.

    Args:
        mock: If True, return MockAgent for testing.

    Returns:
        Initialized agent instance.
    """
    config = get_config()
    computer = get_computer(config, mock=mock)
    await computer.connect()

    if mock:
        return MockAgent(computer, config)

    agent = DeskPilotAgent(computer, config)
    await agent.initialize()
    return agent
