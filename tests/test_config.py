"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from insta_trend_tool.config import Config, load_config


class TestConfig:
    """Test Config dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.instagram_username is None
        assert config.instagram_password is None
        assert config.slack_webhook_url is None
        assert config.default_top_count == 50
        assert config.default_days_back == 30
        assert config.request_delay_min == 2.0
        assert config.request_delay_max == 5.0
        assert config.max_retries == 3
        assert config.retry_delay == 10.0
        assert config.output_dir == Path("output")
        assert config.log_level == "INFO"
        assert config.log_file is None


class TestLoadConfig:
    """Test configuration loading."""
    
    def test_load_config_defaults(self):
        """Test loading configuration with defaults."""
        config = load_config()
        
        assert isinstance(config, Config)
        assert config.default_top_count == 50
    
    def test_load_config_from_yaml(self):
        """Test loading configuration from YAML file."""
        yaml_content = {
            "default_top_count": 100,
            "default_days_back": 14,
            "request_delay_min": 1.0,
            "log_level": "DEBUG",
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(yaml_content, f)
            yaml_path = f.name
        
        try:
            config = load_config(yaml_path)
            
            assert config.default_top_count == 100
            assert config.default_days_back == 14
            assert config.request_delay_min == 1.0
            assert config.log_level == "DEBUG"
            # Unchanged values should keep defaults
            assert config.request_delay_max == 5.0
        finally:
            os.unlink(yaml_path)
    
    def test_load_config_env_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("DEFAULT_TOP_COUNT", "75")
        monkeypatch.setenv("INSTAGRAM_USERNAME", "testuser")
        monkeypatch.setenv("REQUEST_DELAY_MIN", "3.5")
        
        config = load_config()
        
        assert config.default_top_count == 75
        assert config.instagram_username == "testuser"
        assert config.request_delay_min == 3.5
    
    def test_load_config_nonexistent_file(self):
        """Test loading configuration with nonexistent file."""
        config = load_config("nonexistent.yml")
        
        # Should fall back to defaults
        assert config.default_top_count == 50
    
    def test_load_config_invalid_yaml(self):
        """Test loading configuration with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            yaml_path = f.name
        
        try:
            # Should not raise exception, fall back to defaults
            config = load_config(yaml_path)
            assert config.default_top_count == 50
        finally:
            os.unlink(yaml_path)
    
    def test_output_dir_path_conversion(self):
        """Test that output_dir is converted to Path object."""
        yaml_content = {"output_dir": "custom/output"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(yaml_content, f)
            yaml_path = f.name
        
        try:
            config = load_config(yaml_path)
            assert isinstance(config.output_dir, Path)
            assert str(config.output_dir) == "custom/output"
        finally:
            os.unlink(yaml_path)