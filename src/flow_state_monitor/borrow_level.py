"""
Borrow rate level detection module.

This module provides functionality to detect high borrow rate levels that
indicate forced buying pressure from short covering.
"""

from typing import Tuple


def detect_borrow_level(
    borrow_rate: float,
    high_threshold: float = 10.0,
    medium_threshold: float = 5.0
) -> Tuple[str, dict]:
    """
    Detect borrow rate level significance.
    
    Analyzes the current borrow rate to determine if it indicates forced
    buying pressure. High borrow rates suggest shorts are under pressure.
    
    Args:
        borrow_rate: Current borrow rate as percentage (e.g., 15.5 for 15.5%)
        high_threshold: Threshold for high borrow rate (default: 10.0%)
        medium_threshold: Threshold for medium borrow rate (default: 5.0%)
        
    Returns:
        Tuple of (level: str, details: dict)
        Level is one of: "HIGH", "MEDIUM", "LOW"
        Details dict contains:
            - borrow_rate: The input borrow rate
            - level: The detected level
            - high_threshold: The high threshold used
            - medium_threshold: The medium threshold used
            
    Raises:
        ValueError: If borrow_rate is negative or thresholds are invalid
    """
    if borrow_rate < 0:
        raise ValueError("Borrow rate cannot be negative")
    
    if high_threshold <= medium_threshold:
        raise ValueError("High threshold must be greater than medium threshold")
    
    if borrow_rate >= high_threshold:
        level = "HIGH"
    elif borrow_rate >= medium_threshold:
        level = "MEDIUM"
    else:
        level = "LOW"
    
    details = {
        "borrow_rate": borrow_rate,
        "level": level,
        "high_threshold": high_threshold,
        "medium_threshold": medium_threshold,
    }
    
    return level, details
