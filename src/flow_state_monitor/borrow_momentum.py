"""
Borrow rate momentum detection module.

This module provides functionality to detect momentum in borrow rate changes
over a period of time, indicating sustained pressure trends.

Uses EMA (Exponential Moving Average) on daily deltas as specified in the design specification.
"""

from typing import List, Tuple


def calculate_ema(values: List[float], span: int) -> float:
    """
    Calculate exponential moving average of a series.

    Args:
        values: List of values (most recent last)
        span: EMA span parameter (typically 3 or 5)

    Returns:
        EMA value

    Note:
        Uses alpha = 2/(span+1) weighting
    """
    if len(values) == 0:
        raise ValueError("Cannot calculate EMA of empty list")

    alpha = 2.0 / (span + 1)
    ema = values[0]

    for value in values[1:]:
        ema = alpha * value + (1 - alpha) * ema

    return ema


def calculate_momentum(borrow_rates: List[float], ema_span: int = 3) -> float:
    """
    Calculate borrow rate momentum using EMA of daily deltas.

    Per design specification:
    - ΔB(t) = borrow_rate(t) - borrow_rate(t-1)
    - Momentum = EMA(ΔB)

    Args:
        borrow_rates: List of daily borrow rates (most recent last)
        ema_span: EMA span for smoothing (default: 3, can use 5)

    Returns:
        Smoothed momentum (EMA of daily deltas) in percentage points per day

    Raises:
        ValueError: If borrow_rates list has fewer than 2 values
    """
    if len(borrow_rates) < 2:
        raise ValueError("Need at least 2 borrow rates to calculate momentum")

    for rate in borrow_rates:
        if rate < 0:
            raise ValueError("Borrow rates cannot be negative")

    # Calculate daily deltas: ΔB(t) = borrow_rate(t) - borrow_rate(t-1)
    deltas = [borrow_rates[i] - borrow_rates[i-1] for i in range(1, len(borrow_rates))]

    # Apply EMA to deltas
    if len(deltas) == 0:
        return 0.0

    momentum = calculate_ema(deltas, span=ema_span)

    return momentum


def detect_borrow_momentum(
    borrow_rates: List[float],
    positive_threshold: float = 1.0,
    negative_threshold: float = -1.0,
    ema_span: int = 3
) -> Tuple[str, dict]:
    """
    Detect momentum in borrow rate changes using EMA of daily deltas.

    Analyzes the trend in borrow rate changes over multiple days to identify
    sustained increases or decreases in forced buying pressure.

    Per COPILOT_SPEC.md:
    - Uses EMA on ΔB (daily deltas)
    - Default ema_span = 3 (can be overridden to 5)

    Args:
        borrow_rates: List of daily borrow rates (most recent last)
        positive_threshold: Threshold for positive momentum (pct points per day)
        negative_threshold: Threshold for negative momentum (pct points per day, negative)
        ema_span: EMA span for smoothing (default: 3)

    Returns:
        Tuple of (momentum_type: str, details: dict)
        Momentum type is one of: "POSITIVE", "NEGATIVE", "NEUTRAL"
        Details dict contains:
            - momentum: The calculated momentum value (EMA of deltas)
            - momentum_type: The detected momentum type
            - period_days: Number of days analyzed
            - start_rate: First borrow rate in period
            - end_rate: Last borrow rate in period
            - ema_span: EMA span used

    Raises:
        ValueError: If insufficient data or invalid parameters
    """
    if len(borrow_rates) < 2:
        raise ValueError("Need at least 2 borrow rates for momentum analysis")

    if positive_threshold <= 0:
        raise ValueError("Positive threshold must be positive")

    if negative_threshold >= 0:
        raise ValueError("Negative threshold must be negative")

    momentum = calculate_momentum(borrow_rates, ema_span=ema_span)

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
        "ema_span": ema_span,
    }

    return momentum_type, details
