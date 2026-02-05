"""Configuration management for DeskPilot."""

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NativeConfig(BaseModel):
    """Native control configuration."""

    screenshot_delay: float = 0.5
    typing_interval: float = 0.05
    click_pause: float = 0.1


class WinAppDriverConfig(BaseModel):
    """WinAppDriver configuration (Windows only)."""

    enabled: bool = True
    path: str = r"C:\Program Files\Windows Application Driver\WinAppDriver.exe"
    port: int = 4723
    auto_start: bool = True
    timeout: float = 10.0


class WindowsConfig(BaseModel):
    """Windows-specific configuration with WinAppDriver support."""

    winappdriver: WinAppDriverConfig = Field(default_factory=WinAppDriverConfig)
    screenshot_delay: float = 0.5
    typing_interval: float = 0.05
    click_pause: float = 0.1
    fallback_on_failure: bool = True


class ModelConfig(BaseModel):
    """AI model configuration."""

    provider: str = "ollama"
    name: str = "qwen2.5:3b"
    base_url: str = "http://localhost:11434"


class AgentConfig(BaseModel):
    """Agent behavior configuration."""

    max_steps: int = 50
    screenshot_on_step: bool = True
    verbose: bool = True


class OpenClawConfig(BaseModel):
    """OpenClaw integration configuration."""

    enabled: bool = True
    skill_path: str = "~/.openclaw/skills/computer-use"
    daemon_url: str = "http://localhost:3000"
    auto_start_tui: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    file: str | None = None
    screenshots_dir: str = "./screenshots"


class DeskPilotConfig(BaseSettings):
    """Main DeskPilot configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DESKPILOT_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    model: ModelConfig = Field(default_factory=ModelConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    openclaw: OpenClawConfig = Field(default_factory=OpenClawConfig)
    native: NativeConfig = Field(default_factory=NativeConfig)
    windows: WindowsConfig = Field(default_factory=WindowsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def find_config_file() -> Path | None:
    """Find the configuration file.

    Search order:
    1. DESKPILOT_CONFIG environment variable
    2. ./config/local.yaml
    3. ./config/default.yaml
    4. Package default config
    """
    # Check environment variable
    env_config = os.environ.get("DESKPILOT_CONFIG")
    if env_config:
        path = Path(env_config)
        if path.exists():
            return path

    # Check local config
    local_config = Path("config/local.yaml")
    if local_config.exists():
        return local_config

    # Check default config
    default_config = Path("config/default.yaml")
    if default_config.exists():
        return default_config

    # Check package config
    package_config = Path(__file__).parent.parent.parent.parent / "config" / "default.yaml"
    if package_config.exists():
        return package_config

    return None


def load_config(config_path: Path | str | None = None) -> DeskPilotConfig:
    """Load configuration from YAML file with environment variable overrides.

    Args:
        config_path: Path to config file. If None, searches default locations.

    Returns:
        DeskPilotConfig instance with merged settings.
    """
    config_data = {}

    # Find config file
    path = Path(config_path) if config_path else find_config_file()

    # Load YAML if found
    if path and path.exists():
        with open(path) as f:
            config_data = yaml.safe_load(f) or {}

    # Create config with YAML data as defaults, env vars override
    return DeskPilotConfig(**config_data)


def save_config(config: DeskPilotConfig, path: Path | str) -> None:
    """Save configuration to YAML file.

    Args:
        config: Configuration to save.
        path: Path to save to.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict, excluding defaults that match the model defaults
    data = config.model_dump(mode="json")

    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def get_config() -> DeskPilotConfig:
    """Get the current configuration (singleton pattern).

    Returns:
        DeskPilotConfig instance.
    """
    if not hasattr(get_config, "_instance"):
        get_config._instance = load_config()
    return get_config._instance


def reload_config(config_path: Path | str | None = None) -> DeskPilotConfig:
    """Reload configuration from file.

    Args:
        config_path: Path to config file.

    Returns:
        New DeskPilotConfig instance.
    """
    get_config._instance = load_config(config_path)
    return get_config._instance
