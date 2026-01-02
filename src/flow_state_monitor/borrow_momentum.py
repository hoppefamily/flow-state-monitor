"""
Borrow rate momentum detection module.

This module provides functionality to detect momentum in borrow rate changes
over a period of time, indicating sustained pressure trends.
"""

from typing import List, Tuple


def calculate_momentum(borrow_rates: List[float]) -> float:
    """
    Calculate borrow rate momentum.
    
    Momentum is the average daily change in borrow rate over the period.
    Positive momentum indicates sustained increases, negative indicates decreases.
    
    Args:
        borrow_rates: List of daily borrow rates (most recent last)
        
    Returns:
        Average daily change in borrow rate (percentage points per day)
        
    Raises:
        ValueError: If borrow_rates list has fewer than 2 values
    """
    if len(borrow_rates) < 2:
        raise ValueError("Need at least 2 borrow rates to calculate momentum")
    
    for rate in borrow_rates:
        if rate < 0:
            raise ValueError("Borrow rates cannot be negative")
    
    # Calculate total change and divide by number of periods
    total_change = borrow_rates[-1] - borrow_rates[0]
    num_periods = len(borrow_rates) - 1
    
    return total_change / num_periods


def detect_borrow_momentum(
    borrow_rates: List[float],
    positive_threshold: float = 1.0,
    negative_threshold: float = -1.0
) -> Tuple[str, dict]:
    """
    Detect momentum in borrow rate changes.
    
    Analyzes the trend in borrow rate changes over multiple days to identify
    sustained increases or decreases in forced buying pressure.
    
    Args:
        borrow_rates: List of daily borrow rates (most recent last)
        positive_threshold: Threshold for positive momentum (pct points per day)
        negative_threshold: Threshold for negative momentum (pct points per day, negative)
        
    Returns:
        Tuple of (momentum_type: str, details: dict)
        Momentum type is one of: "POSITIVE", "NEGATIVE", "NEUTRAL"
        Details dict contains:
            - momentum: The calculated momentum value
            - momentum_type: The detected momentum type
            - period_days: Number of days analyzed
            - start_rate: First borrow rate in period
            - end_rate: Last borrow rate in period
            
    Raises:
        ValueError: If insufficient data or invalid parameters
    """
    if len(borrow_rates) < 2:
        raise ValueError("Need at least 2 borrow rates for momentum analysis")
    
    if positive_threshold <= 0:
        raise ValueError("Positive threshold must be positive")
    
    if negative_threshold >= 0:
        raise ValueError("Negative threshold must be negative")
    
    momentum = calculate_momentum(borrow_rates)
    
    if momentum >= positive_threshold:
        momentum_type = "POSITIVE"
    elif momentum <= negative_threshold:
        momentum_type = "NEGATIVE"
    else:
        momentum_type = "NEUTRAL"
    
    details = {
        "momentum": momentum,
        "momentum_type": momentum_type,
        "period_days": len(borrow_rates) - 1,
        "start_rate": borrow_rates[0],
        "end_rate": borrow_rates[-1],
        "positive_threshold": positive_threshold,
        "negative_threshold": negative_threshold,
    }
    
    return momentum_type, details
