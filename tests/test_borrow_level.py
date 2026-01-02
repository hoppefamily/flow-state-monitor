"""Tests for borrow level detection module."""

import pytest
from flow_state_monitor.borrow_level import detect_borrow_level


def test_high_borrow_level():
    """Test detection of high borrow rate level."""
    level, details = detect_borrow_level(15.0)
    
    assert level == "HIGH"
    assert details["level"] == "HIGH"
    assert details["borrow_rate"] == 15.0


def test_medium_borrow_level():
    """Test detection of medium borrow rate level."""
    level, details = detect_borrow_level(7.5)
    
    assert level == "MEDIUM"
    assert details["level"] == "MEDIUM"
    assert details["borrow_rate"] == 7.5


def test_low_borrow_level():
    """Test detection of low borrow rate level."""
    level, details = detect_borrow_level(2.0)
    
    assert level == "LOW"
    assert details["level"] == "LOW"
    assert details["borrow_rate"] == 2.0


def test_borrow_level_at_high_threshold():
    """Test borrow rate exactly at high threshold."""
    level, details = detect_borrow_level(10.0, high_threshold=10.0)
    
    assert level == "HIGH"


def test_borrow_level_at_medium_threshold():
    """Test borrow rate exactly at medium threshold."""
    level, details = detect_borrow_level(5.0, medium_threshold=5.0)
    
    assert level == "MEDIUM"


def test_custom_thresholds():
    """Test with custom threshold values."""
    level, details = detect_borrow_level(12.0, high_threshold=15.0, medium_threshold=8.0)
    
    assert level == "MEDIUM"


def test_negative_borrow_rate():
    """Test that negative borrow rate raises ValueError."""
    with pytest.raises(ValueError, match="cannot be negative"):
        detect_borrow_level(-1.0)


def test_invalid_thresholds():
    """Test that invalid threshold configuration raises ValueError."""
    with pytest.raises(ValueError, match="greater than medium"):
        detect_borrow_level(5.0, high_threshold=5.0, medium_threshold=10.0)
