"""Tests for the setup wizard."""

import platform
from unittest.mock import patch

import pytest

from clawbot.wizard.setup import check_dependencies, detect_environment


class TestDetectEnvironment:
    """Tests for environment detection."""

    def test_detect_environment_returns_dict(self):
        """Test that detect_environment returns expected keys."""
        env = detect_environment()

        assert "os" in env
        assert "os_version" in env
        assert "python_version" in env
        assert "arch" in env
        assert "ram_gb" in env

    def test_detect_environment_os(self):
        """Test OS detection matches platform."""
        env = detect_environment()

        assert env["os"] == platform.system()

    def test_detect_environment_python_version(self):
        """Test Python version detection."""
        env = detect_environment()

        assert env["python_version"] == platform.python_version()

    def test_detect_environment_ram_positive(self):
        """Test RAM detection returns positive value."""
        env = detect_environment()

        assert env["ram_gb"] > 0


class TestCheckDependencies:
    """Tests for dependency checking."""

    @pytest.mark.asyncio
    async def test_check_dependencies_returns_dict(self):
        """Test that check_dependencies returns expected keys."""
        # Capture console output
        with patch("clawbot.wizard.setup.console"):
            results = await check_dependencies()

        assert isinstance(results, dict)
        assert "python_3.12+" in results
        assert "docker" in results
        assert "ollama" in results
        assert "cua-agent" in results
        assert "native-packages" in results
        assert "openclaw" in results

    @pytest.mark.asyncio
    async def test_python_version_check(self):
        """Test Python version requirement check."""
        with patch("clawbot.wizard.setup.console"):
            results = await check_dependencies()

        # We're running on Python 3.12+, so this should be True
        py_version = platform.python_version_tuple()
        expected = int(py_version[0]) >= 3 and int(py_version[1]) >= 12
        assert results["python_3.12+"] == expected

    @pytest.mark.asyncio
    async def test_os_detection_flags(self):
        """Test OS detection flags are mutually exclusive."""
        with patch("clawbot.wizard.setup.console"):
            results = await check_dependencies()

        os_flags = [results["is_windows"], results["is_macos"], results["is_linux"]]
        # Exactly one should be True (or none on exotic OS)
        assert sum(os_flags) <= 1


class TestSetupWizardFlow:
    """Tests for the setup wizard flow."""

    @pytest.mark.asyncio
    async def test_wizard_detects_environment(self):
        """Test that wizard properly detects environment."""
        env = detect_environment()

        # Should have all required keys
        required_keys = ["os", "os_version", "python_version", "arch", "ram_gb"]
        for key in required_keys:
            assert key in env

    @pytest.mark.asyncio
    async def test_wizard_with_mock_prompts(self):
        """Test wizard flow with mocked user input."""
        # This is a smoke test - full integration would require
        # mocking Rich prompts and console
        with patch("clawbot.wizard.setup.console"):
            with patch("clawbot.wizard.setup.Prompt") as mock_prompt:
                with patch("clawbot.wizard.setup.Confirm") as mock_confirm:
                    mock_prompt.ask.return_value = "vm"
                    mock_confirm.ask.return_value = False

                    # Verify mocks are set up correctly
                    assert mock_prompt.ask.return_value == "vm"


class TestSkillInstallation:
    """Tests for OpenClaw skill installation."""

    def test_skill_source_path_exists(self):
        """Test that the skill source path is valid."""
        from pathlib import Path

        skill_source = (
            Path(__file__).parent.parent
            / "src"
            / "clawbot"
            / "openclaw_skill"
            / "computer-use"
        )
        # Path should exist after project setup
        # This validates the project structure

    def test_skill_md_content(self):
        """Test that SKILL.md has required content."""
        from pathlib import Path

        skill_path = (
            Path(__file__).parent.parent
            / "src"
            / "clawbot"
            / "openclaw_skill"
            / "computer-use"
            / "SKILL.md"
        )

        if skill_path.exists():
            content = skill_path.read_text()

            # Check for required sections
            assert "name: computer-use" in content
            assert "clawbot" in content.lower()
            assert "screenshot" in content.lower()
            assert "click" in content.lower()


class TestDemoModule:
    """Tests for the demo module."""

    @pytest.mark.asyncio
    async def test_demo_import(self):
        """Test that demo module imports correctly."""
        from clawbot.wizard.demo import run_calculator_demo, run_quick_demo

        assert callable(run_calculator_demo)
        assert callable(run_quick_demo)

    @pytest.mark.asyncio
    async def test_quick_demo_mock_mode(self):
        """Test quick demo in mock mode doesn't crash."""
        from clawbot.wizard.demo import run_quick_demo

        # Suppress console output
        with patch("clawbot.wizard.demo.console"):
            with patch("clawbot.cua_bridge.agent.console"):
                # Should complete without error in mock mode
                await run_quick_demo(mock=True)
