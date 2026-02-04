"""Configuration management for DeskPilot."""

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VMConfig(BaseModel):
    """VM deployment configuration."""

    os_type: Literal["macos", "linux", "windows", "android"] = "macos"
    provider_type: Literal["lume", "docker", "cloud"] = "lume"
    display: str = "1920x1080"
    ram_size: str = "8G"
    cpu_cores: int = 4
    disk_size: str = "64G"
    vnc_port: int = 8006
    api_port: int = 5000
    storage_path: str = "./storage"


class NativeConfig(BaseModel):
    """Native Windows deployment configuration."""

    screenshot_delay: float = 0.5
    typing_interval: float = 0.05
    click_pause: float = 0.1


class DeploymentConfig(BaseModel):
    """Deployment mode configuration."""

    mode: Literal["vm", "native"] = "vm"


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

    enabled: bool = False
    skill_path: str = "~/.openclaw/skills/computer-use"
    daemon_url: str = "http://localhost:3000"


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

    deployment: DeploymentConfig = Field(default_factory=DeploymentConfig)
    vm: VMConfig = Field(default_factory=VMConfig)
    native: NativeConfig = Field(default_factory=NativeConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    openclaw: OpenClawConfig = Field(default_factory=OpenClawConfig)
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
    if config_path:
        path = Path(config_path)
    else:
        path = find_config_file()

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
