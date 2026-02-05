"""AI Agent wrapper for computer automation."""

from __future__ import annotations

import asyncio
import base64
import contextlib
import io
import json
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import httpx
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


SYSTEM_PROMPT = """You are a computer automation agent. You can see the screen and control the mouse and keyboard.

Available actions:
- click(x, y): Click at screen coordinates
- double_click(x, y): Double-click at coordinates
- type(text): Type text into the focused element
- press(key): Press a key (enter, escape, tab, etc.)
- hotkey(keys): Press key combination (e.g., "ctrl+c", "cmd+space")
- launch(app): Launch an application by name
- done(result): Task is complete, provide the result

Respond with JSON in this format:
{
    "reasoning": "Brief explanation of what you see and plan to do",
    "action": "action_name",
    "params": {"param1": "value1"}
}

Important:
- Coordinates are in pixels from top-left (0,0)
- Look carefully at the screenshot to find UI elements
- Use "done" when the task is complete
- Be precise with click coordinates - aim for the center of buttons/elements
"""


class OllamaAgent:
    """AI Agent using Ollama directly for vision + control."""

    def __init__(
        self,
        computer: BaseComputer,
        config: DeskPilotConfig | None = None,
    ) -> None:
        self.computer = computer
        self.config = config or get_config()
        self._client = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the Ollama client."""
        if self._initialized:
            return

        self._client = httpx.AsyncClient(
            base_url=self.config.model.base_url,
            timeout=120.0,
        )
        self._initialized = True

    async def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64."""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def _call_ollama(self, prompt: str, image: Image.Image | None = None) -> str:
        """Call Ollama API with optional image."""
        if not self._client:
            raise RuntimeError("Agent not initialized")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        # Build user message with optional image
        if image:
            image_b64 = await self._encode_image(image)
            messages.append({
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            })
        else:
            messages.append({"role": "user", "content": prompt})

        response = await self._client.post(
            "/api/chat",
            json={
                "model": self.config.model.name,
                "messages": messages,
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")

    def _parse_response(self, response: str) -> dict:
        """Parse JSON response from Ollama."""
        # Try to extract JSON from response
        try:
            # Look for JSON block
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Fallback: return error
        return {
            "reasoning": response,
            "action": "done",
            "params": {"result": "Could not parse response"},
        }

    async def _execute_action(self, action: str, params: dict) -> str:
        """Execute an action on the computer."""
        try:
            if action == "click":
                await self.computer.click(params.get("x", 0), params.get("y", 0))
                return f"Clicked at ({params.get('x')}, {params.get('y')})"

            elif action == "double_click":
                await self.computer.double_click(params.get("x", 0), params.get("y", 0))
                return f"Double-clicked at ({params.get('x')}, {params.get('y')})"

            elif action == "type":
                await self.computer.type_text(params.get("text", ""))
                return f"Typed: {params.get('text')}"

            elif action == "press":
                await self.computer.press_key(params.get("key", ""))
                return f"Pressed: {params.get('key')}"

            elif action == "hotkey":
                keys = params.get("keys", "").split("+")
                await self.computer.hotkey(*keys)
                return f"Pressed hotkey: {params.get('keys')}"

            elif action == "launch":
                # Use spotlight/start menu
                import platform
                if platform.system() == "Darwin":
                    await self.computer.hotkey("cmd", "space")
                    await asyncio.sleep(0.5)
                    await self.computer.type_text(params.get("app", ""))
                    await asyncio.sleep(0.3)
                    await self.computer.press_key("enter")
                elif platform.system() == "Windows":
                    await self.computer.press_key("win")
                    await asyncio.sleep(0.5)
                    await self.computer.type_text(params.get("app", ""))
                    await asyncio.sleep(0.3)
                    await self.computer.press_key("enter")
                else:
                    await self.computer.type_text(params.get("app", ""))
                return f"Launched: {params.get('app')}"

            elif action == "done":
                return params.get("result", "Task completed")

            else:
                return f"Unknown action: {action}"

        except Exception as e:
            return f"Action failed: {e}"

    async def run(
        self,
        task: str,
        verbose: bool | None = None,
    ) -> AsyncIterator[AgentStep]:
        """Run a task and yield steps as they complete."""
        if verbose is None:
            verbose = self.config.agent.verbose

        if not self._initialized:
            await self.initialize()

        step_num = 0
        history = []

        while step_num < self.config.agent.max_steps:
            step_num += 1
            step = AgentStep(step_number=step_num)

            try:
                # Take screenshot
                screenshot = await self.computer.screenshot()
                step.screenshot = screenshot

                # Build prompt
                if step_num == 1:
                    prompt = f"Task: {task}\n\nHere is the current screen. What should I do first?"
                else:
                    history_text = "\n".join([f"Step {h['step']}: {h['action']} -> {h['result']}" for h in history[-5:]])
                    prompt = f"Task: {task}\n\nPrevious actions:\n{history_text}\n\nHere is the current screen. What should I do next?"

                # Call Ollama
                response = await self._call_ollama(prompt, screenshot)
                parsed = self._parse_response(response)

                step.reasoning = parsed.get("reasoning")
                step.action = parsed.get("action")
                step.action_params = parsed.get("params", {})

                # Execute action
                if step.action:
                    result = await self._execute_action(step.action, step.action_params or {})
                    step.result = result
                    history.append({
                        "step": step_num,
                        "action": step.action,
                        "result": result,
                    })

                if verbose:
                    self._print_step(step)

                yield step

                # Check if done
                if step.action == "done":
                    break

                # Small delay between steps
                await asyncio.sleep(self.config.native.screenshot_delay)

            except Exception as e:
                step.error = str(e)
                if verbose:
                    self._print_step(step)
                yield step
                break

    async def execute(self, task: str, verbose: bool | None = None) -> AgentResult:
        """Execute a task and return the complete result."""
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


# Alias for backwards compatibility
DeskPilotAgent = OllamaAgent


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
                action="done",
                action_params={"result": f"Completed: {task}"},
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
        OllamaAgent._print_step(self, step)


async def create_agent(mock: bool = False) -> OllamaAgent | MockAgent:
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

    agent = OllamaAgent(computer, config)
    await agent.initialize()
    return agent
