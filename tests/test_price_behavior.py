"""Tests for price behavior detection module."""

import pytest
from flow_state_monitor.price_behavior import (
    calculate_daily_returns,
    calculate_volatility,
    detect_price_spike,
    detect_abnormal_volatility
)


def test_calculate_daily_returns():
    """Test daily returns calculation."""
    prices = [100.0, 105.0, 103.0, 108.0]
    returns = calculate_daily_returns(prices)
    
    assert len(returns) == 3
    assert returns[0] == pytest.approx(5.0)  # (105-100)/100 * 100
    assert returns[1] == pytest.approx(-1.905, abs=0.01)  # (103-105)/105 * 100
    assert returns[2] == pytest.approx(4.854, abs=0.01)  # (108-103)/103 * 100


def test_calculate_volatility():
    """Test volatility calculation."""
    returns = [1.0, -1.0, 2.0, -2.0, 1.5]
    volatility = calculate_volatility(returns)
    
    assert volatility > 0
    assert isinstance(volatility, float)


def test_detect_price_spike_positive():
    """Test detection of positive price spike."""
    prices = [100.0, 102.0, 103.0, 104.0, 110.0]  # 5.77% spike at end
    detected, details = detect_price_spike(prices, spike_threshold=5.0)
    
    assert detected is True
    assert details["recent_return"] > 5.0


def test_detect_price_spike_negative():
    """Test that no spike is detected with stable prices."""
    prices = [100.0, 101.0, 102.0, 103.0, 104.0]  # Small gains
    detected, details = detect_price_spike(prices, spike_threshold=5.0)
    
    assert detected is False


def test_detect_price_spike_at_threshold():
    """Test spike detection exactly at threshold."""
    prices = [100.0, 105.0]  # Exactly 5% gain
    detected, details = detect_price_spike(prices, spike_threshold=5.0)
    
    assert detected is True


def test_detect_abnormal_volatility_high():
    """Test detection of abnormally high volatility."""
    # Stable prices followed by large move
    prices = [100.0] * 20 + [100.5, 110.0]  # Large spike at end
    detected, details = detect_abnormal_volatility(prices, lookback_period=20)
    
    assert detected is True


def test_detect_abnormal_volatility_normal():
    """Test that normal volatility is not flagged."""
    # Gradually increasing prices
    prices = [100.0 + i * 0.5 for i in range(25)]
    detected, details = detect_abnormal_volatility(prices, lookback_period=20)
    
    assert detected is False


def test_calculate_returns_insufficient_data():
    """Test that insufficient data raises ValueError."""
    with pytest.raises(ValueError, match="at least 2"):
        calculate_daily_returns([100.0])


def test_calculate_returns_negative_price():
    """Test that negative prices raise ValueError."""
    with pytest.raises(ValueError, match="must be positive"):
        calculate_daily_returns([100.0, -50.0])


def test_calculate_volatility_empty():
    """Test that empty returns list raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        calculate_volatility([])


def test_detect_spike_insufficient_data():
    """Test that insufficient data raises ValueError."""
    with pytest.raises(ValueError, match="at least 2"):
        detect_price_spike([100.0])


def test_detect_volatility_insufficient_data():
    """Test that insufficient data raises ValueError."""
    with pytest.raises(ValueError, match="at least"):
        detect_abnormal_volatility([100.0, 101.0], lookback_period=20)
