"""Tests for borrow delta detection module."""

import pytest
from flow_state_monitor.borrow_delta import detect_borrow_delta


def test_increasing_delta():
    """Test detection of increasing borrow rate."""
    change_type, details = detect_borrow_delta(5.0, 8.0)
    
    assert change_type == "INCREASING"
    assert details["change_type"] == "INCREASING"
    assert details["delta"] == 3.0


def test_decreasing_delta():
    """Test detection of decreasing borrow rate."""
    change_type, details = detect_borrow_delta(10.0, 7.0)
    
    assert change_type == "DECREASING"
    assert details["change_type"] == "DECREASING"
    assert details["delta"] == -3.0


def test_stable_delta():
    """Test detection of stable borrow rate."""
    change_type, details = detect_borrow_delta(10.0, 10.5)
    
    assert change_type == "STABLE"
    assert details["change_type"] == "STABLE"


def test_delta_at_increase_threshold():
    """Test delta exactly at increase threshold."""
    change_type, details = detect_borrow_delta(5.0, 7.0, increase_threshold=2.0)
    
    assert change_type == "INCREASING"


def test_delta_at_decrease_threshold():
    """Test delta exactly at decrease threshold."""
    change_type, details = detect_borrow_delta(10.0, 8.0, decrease_threshold=-2.0)
    
    assert change_type == "DECREASING"


def test_custom_thresholds():
    """Test with custom threshold values."""
    change_type, details = detect_borrow_delta(
        10.0, 12.5, 
        increase_threshold=3.0, 
        decrease_threshold=-3.0
    )
    
    assert change_type == "STABLE"


def test_negative_borrow_rates():
    """Test that negative borrow rates raise ValueError."""
    with pytest.raises(ValueError, match="cannot be negative"):
        detect_borrow_delta(-1.0, 5.0)
    
    with pytest.raises(ValueError, match="cannot be negative"):
        detect_borrow_delta(5.0, -1.0)


def test_invalid_increase_threshold():
    """Test that invalid increase threshold raises ValueError."""
    with pytest.raises(ValueError, match="must be positive"):
        detect_borrow_delta(5.0, 8.0, increase_threshold=-1.0)


def test_invalid_decrease_threshold():
    """Test that invalid decrease threshold raises ValueError."""
    with pytest.raises(ValueError, match="must be negative"):
        detect_borrow_delta(5.0, 8.0, decrease_threshold=1.0)
