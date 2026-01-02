"""
Borrow rate delta (change) detection module.

This module provides functionality to detect significant changes in borrow
rates that indicate strengthening or weakening forced buying pressure.
"""

from typing import Tuple


def detect_borrow_delta(
    previous_borrow_rate: float,
    current_borrow_rate: float,
    increase_threshold: float = 2.0,
    decrease_threshold: float = -2.0
) -> Tuple[str, dict]:
    """
    Detect significant changes in borrow rate.
    
    Analyzes the change in borrow rate from previous day to current day.
    Significant increases suggest strengthening pressure, while decreases
    suggest weakening pressure.
    
    Args:
        previous_borrow_rate: Previous day's borrow rate (percentage)
        current_borrow_rate: Current day's borrow rate (percentage)
        increase_threshold: Threshold for significant increase in percentage points
        decrease_threshold: Threshold for significant decrease in percentage points (negative)
        
    Returns:
        Tuple of (change_type: str, details: dict)
        Change type is one of: "INCREASING", "DECREASING", "STABLE"
        Details dict contains:
            - delta: The change in borrow rate (percentage points)
            - previous_rate: Previous borrow rate
            - current_rate: Current borrow rate
            - change_type: The detected change type
            
    Raises:
        ValueError: If borrow rates are negative or thresholds are invalid
    """
    if previous_borrow_rate < 0 or current_borrow_rate < 0:
        raise ValueError("Borrow rates cannot be negative")
    
    if increase_threshold <= 0:
        raise ValueError("Increase threshold must be positive")
    
    if decrease_threshold >= 0:
        raise ValueError("Decrease threshold must be negative")
    
    delta = current_borrow_rate - previous_borrow_rate
    
    if delta >= increase_threshold:
        change_type = "INCREASING"
    elif delta <= decrease_threshold:
        change_type = "DECREASING"
    else:
        change_type = "STABLE"
    
    details = {
        "delta": delta,
        "previous_rate": previous_borrow_rate,
        "current_rate": current_borrow_rate,
        "change_type": change_type,
        "increase_threshold": increase_threshold,
        "decrease_threshold": decrease_threshold,
    }
    
    return change_type, details
