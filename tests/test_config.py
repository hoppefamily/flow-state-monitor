"""Tests for configuration module."""

import pytest
import tempfile
import os
from flow_state_monitor.config import Config


def test_default_config():
    """Test that default configuration is loaded correctly."""
    config = Config()
    
    assert config.get("borrow_level", "high_threshold_percent") == 10.0
    assert config.get("borrow_level", "medium_threshold_percent") == 5.0
    assert config.get("general", "min_data_points") == 6


def test_get_section():
    """Test getting entire configuration section."""
    config = Config()
    
    borrow_level = config.get_section("borrow_level")
    assert "high_threshold_percent" in borrow_level
    assert "medium_threshold_percent" in borrow_level


def test_load_custom_config():
    """Test loading custom configuration from file."""
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
borrow_level:
  high_threshold_percent: 15.0
  medium_threshold_percent: 8.0

general:
  min_data_points: 10
""")
        config_path = f.name
    
    try:
        config = Config(config_path)
        
        assert config.get("borrow_level", "high_threshold_percent") == 15.0
        assert config.get("borrow_level", "medium_threshold_percent") == 8.0
        assert config.get("general", "min_data_points") == 10
    finally:
        os.unlink(config_path)


def test_partial_custom_config():
    """Test that custom config merges with defaults."""
    # Create temporary config file with only partial settings
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
borrow_level:
  high_threshold_percent: 20.0
""")
        config_path = f.name
    
    try:
        config = Config(config_path)
        
        # Custom value
        assert config.get("borrow_level", "high_threshold_percent") == 20.0
        # Default value (not overridden)
        assert config.get("borrow_level", "medium_threshold_percent") == 5.0
    finally:
        os.unlink(config_path)


def test_nonexistent_config_file():
    """Test that nonexistent config file uses defaults."""
    config = Config("/nonexistent/path/to/config.yaml")
    
    # Should fall back to defaults
    assert config.get("borrow_level", "high_threshold_percent") == 10.0


def test_get_nonexistent_key():
    """Test that getting nonexistent key raises KeyError."""
    config = Config()
    
    with pytest.raises(KeyError):
        config.get("nonexistent", "key")


def test_get_section_nonexistent():
    """Test that getting nonexistent section returns empty dict."""
    config = Config()
    
    section = config.get_section("nonexistent")
    assert section == {}
