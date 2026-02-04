"""Tests for configuration management."""

import tempfile
from pathlib import Path

import yaml

from deskpilot.wizard.config import (
    DeskPilotConfig,
    ModelConfig,
    NativeConfig,
    OpenClawConfig,
    load_config,
    save_config,
)


class TestDeskPilotConfig:
    """Tests for DeskPilotConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DeskPilotConfig()

        assert config.model.provider == "ollama"
        assert config.model.name == "qwen2.5:3b"
        assert config.agent.max_steps == 50
        assert config.logging.level == "INFO"
        assert config.openclaw.enabled is True

    def test_nested_config_override(self):
        """Test overriding nested config values."""
        config = DeskPilotConfig(
            model=ModelConfig(name="llama3.2-vision:11b"),
            openclaw=OpenClawConfig(enabled=False),
        )

        assert config.model.name == "llama3.2-vision:11b"
        assert config.openclaw.enabled is False

    def test_native_config_defaults(self):
        """Test native configuration defaults."""
        config = DeskPilotConfig()

        assert config.native.screenshot_delay == 0.5
        assert config.native.typing_interval == 0.05
        assert config.native.click_pause == 0.1

    def test_openclaw_config_defaults(self):
        """Test OpenClaw configuration defaults."""
        config = DeskPilotConfig()

        assert config.openclaw.enabled is True
        assert config.openclaw.auto_start_tui is True
        assert "~/.openclaw/skills/computer-use" in config.openclaw.skill_path


class TestConfigLoadSave:
    """Tests for config loading and saving."""

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        config = DeskPilotConfig(
            model=ModelConfig(name="test-model"),
            native=NativeConfig(typing_interval=0.1),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            save_config(config, config_path)

            # Verify file exists
            assert config_path.exists()

            # Load and verify
            loaded = load_config(config_path)
            assert loaded.model.name == "test-model"
            assert loaded.native.typing_interval == 0.1

    def test_load_partial_config(self):
        """Test loading config with only some values specified."""
        partial_config = {
            "model": {"name": "custom-model"},
            # Other values should use defaults
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            with open(config_path, "w") as f:
                yaml.dump(partial_config, f)

            loaded = load_config(config_path)
            assert loaded.model.name == "custom-model"
            assert loaded.model.provider == "ollama"  # Default
            assert loaded.agent.max_steps == 50  # Default

    def test_load_nonexistent_file(self):
        """Test loading when file doesn't exist returns defaults."""
        config = load_config("/nonexistent/path/config.yaml")

        # Should return defaults
        assert config.model.provider == "ollama"
        assert config.model.name == "qwen2.5:3b"


class TestConfigValidation:
    """Tests for config validation."""

    def test_valid_log_levels(self):
        """Test valid log level values."""
        from deskpilot.wizard.config import LoggingConfig

        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            logging_config = LoggingConfig(level=level)
            assert logging_config.level == level

    def test_native_config_values(self):
        """Test native configuration value handling."""
        native_config = NativeConfig(
            screenshot_delay=1.0,
            typing_interval=0.1,
            click_pause=0.2,
        )

        assert native_config.screenshot_delay == 1.0
        assert native_config.typing_interval == 0.1
        assert native_config.click_pause == 0.2
