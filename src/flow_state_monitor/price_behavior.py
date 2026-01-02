"""
Price behavior detection module.

This module provides functionality to detect price behavior patterns that
indicate forced buying pressure, such as price spikes and abnormal volatility.
"""

from typing import List, Tuple
import math


def calculate_daily_returns(prices: List[float]) -> List[float]:
    """
    Calculate daily percentage returns from price data.
    
    Args:
        prices: List of daily closing prices
        
    Returns:
        List of daily percentage returns
        
    Raises:
        ValueError: If prices list is empty or contains invalid values
    """
    if not prices or len(prices) < 2:
        raise ValueError("Need at least 2 prices to calculate returns")
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] <= 0 or prices[i] <= 0:
            raise ValueError("Prices must be positive")
        ret = (prices[i] - prices[i-1]) / prices[i-1] * 100.0  # Return as percentage
        returns.append(ret)
    
    return returns


def calculate_volatility(returns: List[float]) -> float:
    """
    Calculate standard deviation (volatility) of returns.
    
    Args:
        returns: List of daily returns (as percentages)
        
    Returns:
        Standard deviation of returns
        
    Raises:
        ValueError: If returns list is empty
    """
    if not returns:
        raise ValueError("Returns list cannot be empty")
    
    n = len(returns)
    mean = sum(returns) / n
    variance = sum((r - mean) ** 2 for r in returns) / n
    return math.sqrt(variance)


def detect_price_spike(
    prices: List[float],
    spike_threshold: float = 5.0
) -> Tuple[bool, dict]:
    """
    Detect significant price spike in most recent day.
    
    A price spike suggests forced buying pressure, potentially from shorts
    covering their positions.
    
    Args:
        prices: List of daily closing prices (most recent last)
        spike_threshold: Threshold for significant price increase (percentage)
        
    Returns:
        Tuple of (spike_detected: bool, details: dict)
        Details dict contains:
            - recent_return: Most recent day's return (percentage)
            - spike_threshold: The threshold used
            - spike_magnitude: How many times threshold was exceeded
            
    Raises:
        ValueError: If insufficient data
    """
    if len(prices) < 2:
        raise ValueError("Need at least 2 prices for spike detection")
    
    returns = calculate_daily_returns(prices)
    recent_return = returns[-1]
    
    spike_detected = recent_return >= spike_threshold
    
    details = {
        "recent_return": recent_return,
        "spike_threshold": spike_threshold,
        "spike_magnitude": recent_return / spike_threshold if spike_threshold > 0 else 0,
    }
    
    return spike_detected, details


def detect_abnormal_volatility(
    prices: List[float],
    lookback_period: int = 20,
    threshold_multiplier: float = 2.0
) -> Tuple[bool, dict]:
    """
    Detect abnormally high volatility.
    
    Abnormal volatility can indicate forced buying pressure and uncertainty
    as shorts cover positions.
    
    Args:
        prices: List of daily closing prices (most recent last)
        lookback_period: Days to use for historical volatility baseline
        threshold_multiplier: Multiplier for historical volatility
        
    Returns:
        Tuple of (abnormal_detected: bool, details: dict)
        Details dict contains:
            - recent_return: Most recent day's return (absolute)
            - historical_volatility: Volatility over lookback period
            - threshold: Calculated threshold value
            - volatility_ratio: Recent return / threshold
            
    Raises:
        ValueError: If insufficient data
    """
    if len(prices) < lookback_period + 2:
        raise ValueError(
            f"Need at least {lookback_period + 2} prices for volatility analysis"
        )
    
    returns = calculate_daily_returns(prices)
    
    # Get historical returns (last lookback_period returns, excluding most recent)
    # With lookback_period returns needed for history, we slice to get exactly those
    historical_returns = returns[-(lookback_period + 1):-1]
    recent_return = returns[-1]
    
    # Calculate historical volatility
    hist_vol = calculate_volatility(historical_returns)
    threshold = hist_vol * threshold_multiplier
    
    # Check for abnormal volatility
    abnormal_detected = abs(recent_return) > threshold
    
    details = {
        "recent_return": abs(recent_return),
        "historical_volatility": hist_vol,
        "threshold": threshold,
        "volatility_ratio": abs(recent_return) / threshold if threshold > 0 else 0,
    }
    
    return abnormal_detected, details
