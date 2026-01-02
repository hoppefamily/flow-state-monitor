"""Tests for borrow momentum detection module."""

import pytest
from flow_state_monitor.borrow_momentum import calculate_momentum, detect_borrow_momentum


def test_calculate_momentum_increasing():
    """Test momentum calculation with increasing rates."""
    rates = [5.0, 7.0, 9.0, 11.0, 13.0]
    momentum = calculate_momentum(rates)
    
    assert momentum == 2.0  # (13-5)/4 = 2.0


def test_calculate_momentum_decreasing():
    """Test momentum calculation with decreasing rates."""
    rates = [20.0, 17.0, 14.0, 11.0, 8.0]
    momentum = calculate_momentum(rates)
    
    assert momentum == -3.0  # (8-20)/4 = -3.0


def test_calculate_momentum_stable():
    """Test momentum calculation with stable rates."""
    rates = [10.0, 10.5, 10.2, 10.3, 10.0]
    momentum = calculate_momentum(rates)
    
    assert momentum == 0.0


def test_positive_momentum():
    """Test detection of positive momentum."""
    rates = [5.0, 7.5, 10.0, 12.5, 15.0, 17.5]
    momentum_type, details = detect_borrow_momentum(rates)
    
    assert momentum_type == "POSITIVE"
    assert details["momentum_type"] == "POSITIVE"
    assert details["momentum"] == 2.5


def test_negative_momentum():
    """Test detection of negative momentum."""
    rates = [20.0, 17.0, 14.0, 11.0, 8.0, 5.0]
    momentum_type, details = detect_borrow_momentum(rates)
    
    assert momentum_type == "NEGATIVE"
    assert details["momentum_type"] == "NEGATIVE"
    assert details["momentum"] == -3.0


def test_neutral_momentum():
    """Test detection of neutral momentum."""
    rates = [10.0, 10.2, 10.4, 10.3, 10.5]
    momentum_type, details = detect_borrow_momentum(rates)
    
    assert momentum_type == "NEUTRAL"


def test_momentum_at_positive_threshold():
    """Test momentum exactly at positive threshold."""
    rates = [5.0, 6.0, 7.0, 8.0, 9.0]
    momentum_type, details = detect_borrow_momentum(rates, positive_threshold=1.0)
    
    assert momentum_type == "POSITIVE"


def test_momentum_at_negative_threshold():
    """Test momentum exactly at negative threshold."""
    rates = [10.0, 9.0, 8.0, 7.0, 6.0]
    momentum_type, details = detect_borrow_momentum(rates, negative_threshold=-1.0)
    
    assert momentum_type == "NEGATIVE"


def test_custom_thresholds():
    """Test with custom threshold values."""
    rates = [10.0, 11.5, 13.0, 14.5, 16.0]
    momentum_type, details = detect_borrow_momentum(
        rates,
        positive_threshold=2.0,
        negative_threshold=-2.0
    )
    
    # Momentum is 1.5, which is below positive threshold of 2.0
    assert momentum_type == "NEUTRAL"


def test_insufficient_data():
    """Test that insufficient data raises ValueError."""
    with pytest.raises(ValueError, match="at least 2"):
        detect_borrow_momentum([5.0])


def test_negative_rates():
    """Test that negative rates raise ValueError."""
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_momentum([5.0, 7.0, -1.0, 9.0])


def test_invalid_positive_threshold():
    """Test that invalid positive threshold raises ValueError."""
    with pytest.raises(ValueError, match="must be positive"):
        detect_borrow_momentum([5.0, 6.0, 7.0], positive_threshold=-1.0)


def test_invalid_negative_threshold():
    """Test that invalid negative threshold raises ValueError."""
    with pytest.raises(ValueError, match="must be negative"):
        detect_borrow_momentum([5.0, 6.0, 7.0], negative_threshold=1.0)
