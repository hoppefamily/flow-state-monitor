"""
Signal generation module for entry/exit decisions.

Per COPILOT_SPEC.md:
- Entry (BUY): Both market_state and flow_state flip from OFF to ON within 0-1 days
- Exit (SELL): EMA(ΔB) < -epsilon for 1 full trading day
- Otherwise: HOLD

This module tracks state transitions to detect proper entry/exit timing.
"""

from typing import Dict, List, Tuple


class SignalGenerator:
    """
    Generates BUY/SELL/HOLD signals based on state transitions.

    Tracks historical states to detect transitions and generate signals
    according to COPILOT_SPEC.md rules.
    """

    def __init__(self, epsilon: float = 0.05):
        """
        Initialize signal generator.

        Args:
            epsilon: Deadband for momentum exit signal (default: 0.05 pct pts/day)
        """
        self.epsilon = epsilon
        self.history: List[Dict] = []

    def update(
        self,
        market_state: str,
        flow_state: str,
        borrow_momentum: float,
        borrow_rate: float,
        price: float
    ) -> Tuple[str, str]:
        """
        Update with new state and generate signal.

        Args:
            market_state: Current market state ("ON" or "OFF")
            flow_state: Current flow state ("ON", "WEAKENING", or "OFF")
            borrow_momentum: Current EMA(ΔB) momentum value
            borrow_rate: Current borrow rate
            price: Current price

        Returns:
            Tuple of (signal: str, reason: str)
            Signal is "BUY", "SELL", or "HOLD"
        """
        current = {
            "market_state": market_state,
            "flow_state": flow_state,
            "borrow_momentum": borrow_momentum,
            "borrow_rate": borrow_rate,
            "price": price,
        }

        self.history.append(current)

        # Generate signal based on current state and history
        signal, reason = self._generate_signal()

        return signal, reason

    def _generate_signal(self) -> Tuple[str, str]:
        """
        Generate signal based on current state and transition history.

        Returns:
            Tuple of (signal: str, reason: str)
        """
        if len(self.history) < 2:
            return "HOLD", "Insufficient history for signal generation"

        current = self.history[-1]
        previous = self.history[-2]

        # Check for ENTRY (BUY) signal
        # Conditions:
        # 1. market_state flips OFF → ON
        # 2. flow_state flips OFF → ON
        # 3. Both flips occur same day or within 1 day

        market_flip = (previous["market_state"] == "OFF" and
                      current["market_state"] == "ON")

        flow_flip = (previous["flow_state"] == "OFF" and
                    current["flow_state"] == "ON")

        # Check if both flipped today
        if market_flip and flow_flip:
            return "BUY", (
                f"ENTRY: Both market_state and flow_state transitioned to ON "
                f"(borrow rate: {current['borrow_rate']:.1f}%)"
            )

        # Check if they flipped within 1 day
        if len(self.history) >= 3:
            prev_prev = self.history[-3]

            # Market flipped yesterday, flow flips today
            market_flip_yesterday = (
                prev_prev["market_state"] == "OFF" and
                previous["market_state"] == "ON" and
                current["market_state"] == "ON"
            )

            # Flow flipped yesterday, market flips today
            flow_flip_yesterday = (
                prev_prev["flow_state"] == "OFF" and
                previous["flow_state"] == "ON" and
                current["flow_state"] == "ON"
            )

            if (market_flip_yesterday and flow_flip) or (flow_flip_yesterday and market_flip):
                return "BUY", (
                    f"ENTRY: market_state and flow_state both ON within 1 day "
                    f"(borrow rate: {current['borrow_rate']:.1f}%)"
                )

        # Check for EXIT (SELL) signal
        # Condition: EMA(ΔB) < -epsilon
        # Must hold for 1 full trading day (current + previous)

        current_exit_condition = current["borrow_momentum"] < -self.epsilon
        previous_exit_condition = previous["borrow_momentum"] < -self.epsilon

        if current_exit_condition and previous_exit_condition:
            return "SELL", (
                f"EXIT: Borrow momentum {current['borrow_momentum']:.3f} < "
                f"-epsilon ({-self.epsilon:.3f}) for 1+ day - constraint exhaustion detected"
            )

        # Check if we should HOLD in position or HOLD out of position
        in_position = (
            current["market_state"] == "ON" or
            current["flow_state"] in ["ON", "WEAKENING"]
        )

        if in_position:
            if current["borrow_momentum"] < -self.epsilon:
                # Exit condition met today but not confirmed yet
                return "HOLD", (
                    f"HOLD: Exit condition triggered but awaiting 1-day confirmation "
                    f"(momentum: {current['borrow_momentum']:.3f})"
                )
            else:
                return "HOLD", (
                    f"HOLD: Position active, no exit signal "
                    f"(momentum: {current['borrow_momentum']:.3f}, epsilon: {self.epsilon:.3f})"
                )
        else:
            return "HOLD", (
                f"HOLD: No entry conditions met "
                f"(market={current['market_state']}, flow={current['flow_state']})"
            )

    def reset(self):
        """Reset history."""
        self.history = []
