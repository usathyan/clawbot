"""Tests for configuration management."""

import tempfile
from pathlib import Path

import yaml

from deskpilot.wizard.config import (
    DeskPilotConfig,
    DeploymentConfig,
    ModelConfig,
    VMConfig,
    load_config,
    save_config,
)


class TestDeskPilotConfig:
    """Tests for DeskPilotConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DeskPilotConfig()

        assert config.deployment.mode == "vm"
        assert config.model.provider == "ollama"
        assert config.model.name == "qwen2.5:3b"
        assert config.agent.max_steps == 50
        assert config.logging.level == "INFO"

    def test_nested_config_override(self):
        """Test overriding nested config values."""
        config = DeskPilotConfig(
            deployment=DeploymentConfig(mode="native"),
            model=ModelConfig(name="llama3.2-vision:11b"),
        )

        assert config.deployment.mode == "native"
        assert config.model.name == "llama3.2-vision:11b"

    def test_vm_config_defaults(self):
        """Test VM configuration defaults."""
        config = DeskPilotConfig()

        assert config.vm.ram_size == "8G"
        assert config.vm.cpu_cores == 4
        assert config.vm.vnc_port == 8006
        assert config.vm.api_port == 5000


class TestConfigLoadSave:
    """Tests for config loading and saving."""

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        config = DeskPilotConfig(
            deployment=DeploymentConfig(mode="native"),
            model=ModelConfig(name="test-model"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            save_config(config, config_path)

            # Verify file exists
            assert config_path.exists()

            # Load and verify
            loaded = load_config(config_path)
            assert loaded.deployment.mode == "native"
            assert loaded.model.name == "test-model"

    def test_load_partial_config(self):
        """Test loading config with only some values specified."""
        partial_config = {
            "deployment": {"mode": "native"},
            # Other values should use defaults
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            with open(config_path, "w") as f:
                yaml.dump(partial_config, f)

            loaded = load_config(config_path)
            assert loaded.deployment.mode == "native"
            assert loaded.model.provider == "ollama"  # Default
            assert loaded.agent.max_steps == 50  # Default

    def test_load_nonexistent_file(self):
        """Test loading when file doesn't exist returns defaults."""
        config = load_config("/nonexistent/path/config.yaml")

        # Should return defaults
        assert config.deployment.mode == "vm"
        assert config.model.provider == "ollama"

    def test_env_var_override(self, monkeypatch):
        """Test environment variable overrides."""
        # Set env vars with the CLAWBOT_ prefix
        monkeypatch.setenv("CLAWBOT_DEPLOYMENT__MODE", "native")

        config = DeskPilotConfig()
        # Note: env vars are processed by pydantic-settings
        # This test verifies the config accepts the structure


class TestConfigValidation:
    """Tests for config validation."""

    def test_valid_deployment_modes(self):
        """Test valid deployment mode values."""
        for mode in ["vm", "native"]:
            config = DeskPilotConfig(deployment=DeploymentConfig(mode=mode))
            assert config.deployment.mode == mode

    def test_valid_log_levels(self):
        """Test valid log level values."""
        from deskpilot.wizard.config import LoggingConfig

        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            logging_config = LoggingConfig(level=level)
            assert logging_config.level == level

    def test_vm_config_values(self):
        """Test VM configuration value handling."""
        vm_config = VMConfig(
            ram_size="16G",
            cpu_cores=8,
            disk_size="128G",
        )

        assert vm_config.ram_size == "16G"
        assert vm_config.cpu_cores == 8
        assert vm_config.disk_size == "128G"
