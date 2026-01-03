"""
Market state detection module.

This module detects whether the market is in an elastic state (normal) or
has broken elasticity (structural tension exists).

Per design specification (docs/design_specification.md):
- market_state OFF = market is elastic, no constraint
- market_state ON = elasticity broken (structural tension exists)
"""

from typing import List, Tuple


def detect_market_state(
    borrow_rates: List[float],
    prices: List[float],
    borrow_threshold: float = 5.0,
    momentum_threshold: float = 0.5
) -> Tuple[str, dict]:
    """
    Detect market state (elastic vs structural tension).

    Market transitions from elastic (OFF) to constrained (ON) when:
    - Borrow rates are elevated (> threshold)
    - Momentum is building (positive trend)

    This indicates market structure has shifted from normal to constrained.

    Args:
        borrow_rates: List of daily borrow rates (most recent last)
        prices: List of daily closing prices (most recent last)
        borrow_threshold: Minimum borrow rate to indicate tension (default: 5.0%)
        momentum_threshold: Momentum threshold for tension (default: 0.5 pct pts/day)

    Returns:
        Tuple of (state: str, details: dict)
        State is "ON" (tension) or "OFF" (elastic)
        Details dict contains:
            - state: The market state
            - borrow_rate: Current borrow rate
            - threshold: Borrow rate threshold used
            - reason: Explanation of state determination

    Raises:
        ValueError: If insufficient data
    """
    if len(borrow_rates) < 2:
        raise ValueError("Need at least 2 borrow rates for market state detection")

    current_rate = borrow_rates[-1]

    # Check if borrow rate indicates structural tension
    elevated_borrow = current_rate >= borrow_threshold

    # Calculate recent momentum
    if len(borrow_rates) >= 3:
        recent_delta = borrow_rates[-1] - borrow_rates[-2]
        building_pressure = recent_delta > 0
    else:
        building_pressure = False

    # Determine state
    if elevated_borrow:
        state = "ON"
        reason = f"Borrow rate {current_rate:.1f}% exceeds threshold {borrow_threshold}% - structural tension exists"
    else:
        state = "OFF"
        reason = f"Borrow rate {current_rate:.1f}% below threshold {borrow_threshold}% - market is elastic"

    details = {
        "state": state,
        "borrow_rate": current_rate,
        "threshold": borrow_threshold,
        "elevated_borrow": elevated_borrow,
        "building_pressure": building_pressure,
        "reason": reason,
    }

    return state, details
