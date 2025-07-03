"""Configuration management for Instagram Trend Tool."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""
    
    # Instagram settings
    instagram_username: Optional[str] = None
    instagram_password: Optional[str] = None
    
    # Slack settings
    slack_webhook_url: Optional[str] = None
    
    # Default parameters
    default_top_count: int = 50
    default_days_back: int = 30
    
    # Request delays (seconds)
    request_delay_min: float = 2.0
    request_delay_max: float = 5.0
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 10.0
    
    # Output settings
    output_dir: Path = Path("output")
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None


def load_config(config_file: Optional[str] = None) -> Config:
    """Load configuration from environment variables and config file.
    
    Args:
        config_file: Optional path to YAML config file
        
    Returns:
        Config object with loaded settings
    """
    # Load .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
    
    # Initialize with defaults
    config = Config()
    
    # Load from config file if provided
    if config_file and Path(config_file).exists():
        with open(config_file, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                for key, value in yaml_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
    
    # Override with environment variables
    config.instagram_username = os.getenv("INSTAGRAM_USERNAME", config.instagram_username)
    config.instagram_password = os.getenv("INSTAGRAM_PASSWORD", config.instagram_password)
    config.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", config.slack_webhook_url)
    
    # Parse numeric environment variables
    if default_top := os.getenv("DEFAULT_TOP_COUNT"):
        config.default_top_count = int(default_top)
    
    if default_days := os.getenv("DEFAULT_DAYS_BACK"):
        config.default_days_back = int(default_days)
    
    if delay_min := os.getenv("REQUEST_DELAY_MIN"):
        config.request_delay_min = float(delay_min)
    
    if delay_max := os.getenv("REQUEST_DELAY_MAX"):
        config.request_delay_max = float(delay_max)
    
    # Ensure output directory is Path object
    if isinstance(config.output_dir, str):
        config.output_dir = Path(config.output_dir)
    
    return config


def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        Config object
    """
    if not hasattr(get_config, "_instance"):
        get_config._instance = load_config()
    return get_config._instance