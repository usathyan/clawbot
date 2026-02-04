"""Tests for the CLI module."""


import pytest
from click.testing import CliRunner

from deskpilot.cli import cli


class TestCLI:
    """Tests for CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "DeskPilot" in result.output
        assert "install" in result.output
        assert "demo" in result.output
        assert "screenshot" in result.output
        assert "status" in result.output

    def test_cli_version(self, runner):
        """Test CLI version output."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "deskpilot" in result.output.lower()

    def test_config_command(self, runner):
        """Test config command displays settings."""
        result = runner.invoke(cli, ["config"])

        assert result.exit_code == 0
        assert "Model" in result.output
        assert "OpenClaw" in result.output

    def test_screenshot_help(self, runner):
        """Test screenshot command help."""
        result = runner.invoke(cli, ["screenshot", "--help"])

        assert result.exit_code == 0
        assert "--save" in result.output
        assert "--describe" in result.output

    def test_click_help(self, runner):
        """Test click command help."""
        result = runner.invoke(cli, ["click", "--help"])

        assert result.exit_code == 0
        assert "--target" in result.output
        assert "--button" in result.output
        assert "--double" in result.output

    def test_type_help(self, runner):
        """Test type command help."""
        result = runner.invoke(cli, ["type", "--help"])

        assert result.exit_code == 0
        assert "TEXT" in result.output

    def test_launch_help(self, runner):
        """Test launch command help."""
        result = runner.invoke(cli, ["launch", "--help"])

        assert result.exit_code == 0
        assert "APP" in result.output

    def test_run_help(self, runner):
        """Test run command help."""
        result = runner.invoke(cli, ["run", "--help"])

        assert result.exit_code == 0
        assert "--verbose" in result.output
        assert "TASK" in result.output

    def test_hotkey_help(self, runner):
        """Test hotkey command help."""
        result = runner.invoke(cli, ["hotkey", "--help"])

        assert result.exit_code == 0
        assert "KEYS" in result.output

    def test_install_help(self, runner):
        """Test install command help."""
        result = runner.invoke(cli, ["install", "--help"])

        assert result.exit_code == 0
        assert "--skip-ollama" in result.output
        assert "--skip-openclaw" in result.output
        assert "--model" in result.output

    def test_uninstall_help(self, runner):
        """Test uninstall command help."""
        result = runner.invoke(cli, ["uninstall", "--help"])

        assert result.exit_code == 0

    def test_tui_help(self, runner):
        """Test tui command help."""
        result = runner.invoke(cli, ["tui", "--help"])

        assert result.exit_code == 0
        assert "OpenClaw" in result.output or "TUI" in result.output


class TestCLIWithMock:
    """Tests for CLI commands with mocked backend."""

    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()

    def test_screenshot_mock_mode(self, runner):
        """Test screenshot command in mock mode."""
        result = runner.invoke(cli, ["screenshot", "--mock"])

        assert result.exit_code == 0
        assert "Screenshot" in result.output or "captured" in result.output.lower()

    def test_click_mock_mode(self, runner):
        """Test click command in mock mode."""
        result = runner.invoke(cli, ["click", "100", "200", "--mock"])

        assert result.exit_code == 0
        assert "success" in result.output.lower() or "Click" in result.output

    def test_click_missing_coordinates(self, runner):
        """Test click command fails without coordinates."""
        result = runner.invoke(cli, ["click", "--mock"])

        # Should show error about missing coordinates
        assert "Error" in result.output or result.exit_code != 0

    def test_type_mock_mode(self, runner):
        """Test type command in mock mode."""
        result = runner.invoke(cli, ["type", "Hello", "--mock"])

        assert result.exit_code == 0
        assert "Typed" in result.output or "success" in result.output.lower()

    def test_launch_mock_mode(self, runner):
        """Test launch command in mock mode."""
        result = runner.invoke(cli, ["launch", "Calculator", "--mock"])

        assert result.exit_code == 0
        assert "Launch" in result.output

    def test_press_mock_mode(self, runner):
        """Test press command in mock mode."""
        result = runner.invoke(cli, ["press", "enter", "--mock"])

        assert result.exit_code == 0
        assert "Pressed" in result.output or "enter" in result.output

    def test_hotkey_mock_mode(self, runner):
        """Test hotkey command in mock mode."""
        result = runner.invoke(cli, ["hotkey", "ctrl", "c", "--mock"])

        assert result.exit_code == 0
        assert "Pressed" in result.output or "ctrl" in result.output

    def test_run_mock_mode(self, runner):
        """Test run command in mock mode."""
        result = runner.invoke(cli, ["run", "test task", "--mock"])

        assert result.exit_code == 0
        assert "Task" in result.output or "Completed" in result.output


class TestCLIConfigOption:
    """Tests for CLI config option."""

    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()

    def test_config_option_nonexistent_file(self, runner):
        """Test that nonexistent config file is rejected."""
        result = runner.invoke(cli, ["--config", "/nonexistent/config.yaml", "config"])

        # Click should reject the file since exists=True
        assert result.exit_code != 0

    def test_config_option_with_valid_file(self, runner):
        """Test config option with valid file."""
        import tempfile

        import yaml

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"model": {"name": "custom-model"}}, f)
            config_path = f.name

        try:
            result = runner.invoke(cli, ["--config", config_path, "config"])

            assert result.exit_code == 0
            # Should show the loaded config
            assert "custom-model" in result.output
        finally:
            import os

            os.unlink(config_path)
