"""
Main flow state monitor module.

This module integrates borrow-rate dynamics and price behavior analysis to
detect market flow states driven by forced buying pressure.

Implements COPILOT_SPEC.md:
- Detects market_state (elastic vs constrained)
- Detects flow_state (forced buying pressure)
- Generates BUY/SELL/HOLD signals based on state transitions
"""

from typing import Dict, List, Optional

from .borrow_delta import detect_borrow_delta
from .borrow_level import detect_borrow_level
from .borrow_momentum import detect_borrow_momentum
from .config import Config
from .market_state import detect_market_state
from .price_behavior import detect_abnormal_volatility, detect_price_spike
from .signals import SignalGenerator


class FlowStateMonitor:
    """
    Monitor market flow states driven by forced buying pressure.

    Implements COPILOT_SPEC.md:
    - market_state: Detects elastic vs constrained market conditions
    - flow_state: Detects forced buying pressure (ON/WEAKENING/OFF)
    - Generates BUY/SELL/HOLD signals based on state transitions

    Flow states:
        - ON: Forced buying pressure is active (high borrow rates, rising, price spikes)
        - WEAKENING: Pressure exists but is diminishing (high rates but falling)
        - OFF: No significant forced buying pressure detected

    Market states (per COPILOT_SPEC.md):
        - ON: Market elasticity broken - structural tension exists
        - OFF: Market is elastic - no constraint

    Signals:
        - BUY: Entry when both states flip ON within 0-1 days
        - SELL: Exit when EMA(ΔB) < -epsilon for 1+ day
        - HOLD: No transition detected

    This is NOT a trading signal or prediction tool. It monitors observable
    flow states to support disciplined entry/exit decisions.

    Attributes:
        config: Configuration object containing detection parameters
        signal_generator: Tracks state transitions and generates signals
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the flow state monitor.

        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or Config()

        # Initialize signal generator
        signal_config = self.config.get_section("signals")
        self.signal_generator = SignalGenerator(epsilon=signal_config["epsilon"])

    def analyze(
        self,
        borrow_rates: List[float],
        prices: List[float]
    ) -> Dict:
        """
        Analyze market data to detect flow state and generate signals.

        Implements COPILOT_SPEC.md output requirements:
        - market_state (ON/OFF)
        - flow_state (ON/WEAKENING/OFF)
        - borrow_rate level
        - borrow_rate delta
        - smoothed borrow momentum (EMA)
        - explicit reason for BUY / SELL / HOLD

        Args:
            borrow_rates: List of daily borrow rates in percent (most recent last)
            prices: List of daily closing prices (most recent last)

        Returns:
            Dictionary containing:
                - market_state: Market elasticity state ("ON" or "OFF")
                - flow_state: Overall flow state ("ON", "WEAKENING", "OFF")
                - signal: Trading signal ("BUY", "SELL", "HOLD")
                - signal_reason: Explanation for the signal
                - signals: Dict of individual signal results
                - summary: Human-readable summary

        Raises:
            ValueError: If insufficient data provided
        """
        min_points = self.config.get("general", "min_data_points")
        if len(borrow_rates) < min_points:
            raise ValueError(
                f"Need at least {min_points} borrow rates for analysis"
            )
        if len(prices) < min_points:
            raise ValueError(
                f"Need at least {min_points} prices for analysis"
            )

        signals = {}

        # Detect market state (per COPILOT_SPEC.md)
        try:
            market_config = self.config.get_section("market_state")
            market_state, market_details = detect_market_state(
                borrow_rates,
                prices,
                borrow_threshold=market_config["tension_threshold_percent"]
            )
            signals["market_state"] = {
                "state": market_state,
                "details": market_details
            }
        except Exception as e:
            signals["market_state"] = {
                "state": "UNKNOWN",
                "error": str(e)
            }
            market_state = "UNKNOWN"

        # Analyze current borrow rate level
        try:
            level_config = self.config.get_section("borrow_level")
            level, level_details = detect_borrow_level(
                borrow_rates[-1],
                high_threshold=level_config["high_threshold_percent"],
                medium_threshold=level_config["medium_threshold_percent"]
            )
            signals["borrow_level"] = {
                "level": level,
                "details": level_details
            }
        except Exception as e:
            signals["borrow_level"] = {
                "level": "UNKNOWN",
                "error": str(e)
            }

        # Analyze borrow rate delta (change)
        try:
            delta_config = self.config.get_section("borrow_delta")
            change_type, delta_details = detect_borrow_delta(
                borrow_rates[-2],
                borrow_rates[-1],
                increase_threshold=delta_config["increase_threshold_pct_points"],
                decrease_threshold=delta_config["decrease_threshold_pct_points"]
            )
            signals["borrow_delta"] = {
                "change_type": change_type,
                "details": delta_details
            }
        except Exception as e:
            signals["borrow_delta"] = {
                "change_type": "UNKNOWN",
                "error": str(e)
            }

        # Analyze borrow rate momentum (EMA-based per COPILOT_SPEC.md)
        try:
            momentum_config = self.config.get_section("borrow_momentum")
            lookback = momentum_config["lookback_period"]
            ema_span = momentum_config.get("ema_span", 3)
            # Use available data if less than lookback period
            momentum_data = borrow_rates[-min(lookback+1, len(borrow_rates)):]

            momentum_type, momentum_details = detect_borrow_momentum(
                momentum_data,
                positive_threshold=momentum_config["positive_threshold_pct_points"],
                negative_threshold=momentum_config["negative_threshold_pct_points"],
                ema_span=ema_span
            )
            signals["borrow_momentum"] = {
                "momentum_type": momentum_type,
                "details": momentum_details
            }
            borrow_momentum_value = momentum_details["momentum"]
        except Exception as e:
            signals["borrow_momentum"] = {
                "momentum_type": "UNKNOWN",
                "error": str(e)
            }
            borrow_momentum_value = 0.0

        # Analyze price spike
        try:
            price_config = self.config.get_section("price_behavior")
            spike_detected, spike_details = detect_price_spike(
                prices,
                spike_threshold=price_config["spike_threshold_percent"]
            )
            signals["price_spike"] = {
                "detected": spike_detected,
                "details": spike_details
            }
        except Exception as e:
            signals["price_spike"] = {
                "detected": False,
                "error": str(e)
            }

        # Analyze abnormal volatility
        try:
            price_config = self.config.get_section("price_behavior")
            volatility_detected, volatility_details = detect_abnormal_volatility(
                prices,
                lookback_period=price_config["volatility_lookback_period"],
                threshold_multiplier=price_config["volatility_threshold_multiplier"]
            )
            signals["abnormal_volatility"] = {
                "detected": volatility_detected,
                "details": volatility_details
            }
        except Exception as e:
            signals["abnormal_volatility"] = {
                "detected": False,
                "error": str(e)
            }

        # Determine overall flow state
        flow_state = self._determine_flow_state(signals)

        # Generate signal (BUY/SELL/HOLD) based on state transitions
        try:
            signal, signal_reason = self.signal_generator.update(
                market_state=market_state,
                flow_state=flow_state,
                borrow_momentum=borrow_momentum_value,
                borrow_rate=borrow_rates[-1],
                price=prices[-1]
            )
        except Exception as e:
            signal = "HOLD"
            signal_reason = f"Signal generation error: {str(e)}"

        # Generate summary
        summary = self._generate_summary(market_state, flow_state, signal, signal_reason, signals)

        return {
            "market_state": market_state,
            "flow_state": flow_state,
            "signal": signal,
            "signal_reason": signal_reason,
            "signals": signals,
            "summary": summary
        }

    def _determine_flow_state(self, signals: Dict) -> str:
        """
        Determine overall flow state from individual signals.

        Logic:
        - ON: High/medium borrow level + (positive momentum OR increasing delta OR price spike)
        - WEAKENING: High/medium borrow level + negative momentum or decreasing delta
        - OFF: Low borrow level or no supporting signals

        Args:
            signals: Dictionary of individual signal results

        Returns:
            Flow state: "ON", "WEAKENING", or "OFF"
        """
        borrow_level = signals.get("borrow_level", {}).get("level", "UNKNOWN")
        change_type = signals.get("borrow_delta", {}).get("change_type", "UNKNOWN")
        momentum_type = signals.get("borrow_momentum", {}).get("momentum_type", "UNKNOWN")
        price_spike = signals.get("price_spike", {}).get("detected", False)

        # Check if borrow level is significant
        high_borrow = borrow_level in ["HIGH", "MEDIUM"]

        # Check for strengthening signals
        strengthening = (
            momentum_type == "POSITIVE" or
            change_type == "INCREASING" or
            price_spike
        )

        # Check for weakening signals
        weakening = (
            momentum_type == "NEGATIVE" or
            change_type == "DECREASING"
        )

        # Determine state
        if high_borrow and strengthening:
            return "ON"
        elif high_borrow and weakening:
            return "WEAKENING"
        elif high_borrow:
            # High borrow but no clear direction
            return "ON"
        else:
            return "OFF"

    def _generate_summary(
        self,
        market_state: str,
        flow_state: str,
        signal: str,
        signal_reason: str,
        signals: Dict
    ) -> str:
        """
        Generate human-readable summary per COPILOT_SPEC.md output requirements.

        Must include:
        - market_state (ON/OFF)
        - flow_state (ON/OFF)
        - borrow_rate level
        - borrow_rate delta
        - smoothed borrow momentum
        - explicit reason for BUY / SELL / HOLD

        Args:
            market_state: Market state
            flow_state: Flow state
            signal: Trading signal
            signal_reason: Explanation for signal
            signals: Dictionary of individual signal results

        Returns:
            Summary string
        """
        # Extract values from signals
        borrow_rate = signals.get("borrow_level", {}).get("details", {}).get("borrow_rate", 0)
        borrow_level = signals.get("borrow_level", {}).get("level", "UNKNOWN")

        delta_details = signals.get("borrow_delta", {}).get("details", {})
        delta = delta_details.get("delta", 0)

        momentum_details = signals.get("borrow_momentum", {}).get("details", {})
        momentum = momentum_details.get("momentum", 0)
        ema_span = momentum_details.get("ema_span", 3)

        # Build summary per COPILOT_SPEC.md format
        lines = []
        lines.append("=" * 60)
        lines.append("FLOW STATE MONITOR - ANALYSIS (per COPILOT_SPEC.md)")
        lines.append("=" * 60)
        lines.append("")

        # Core states
        lines.append(f"MARKET STATE: {market_state}")
        if market_state == "ON":
            lines.append("  → Elasticity broken - structural tension exists")
        else:
            lines.append("  → Market is elastic - no constraint")
        lines.append("")

        lines.append(f"FLOW STATE: {flow_state}")
        if flow_state == "ON":
            lines.append("  → Forced buying pressure ACTIVE")
        elif flow_state == "WEAKENING":
            lines.append("  → Forced buying pressure DIMINISHING")
        else:
            lines.append("  → No significant forced buying pressure")
        lines.append("")

        # Borrow rate metrics
        lines.append("BORROW RATE METRICS:")
        lines.append(f"  • Level: {borrow_rate:.2f}% ({borrow_level})")
        lines.append(f"  • Delta: {delta:+.2f} pct points")
        lines.append(f"  • Smoothed Momentum (EMA-{ema_span}): {momentum:+.3f} pct points/day")
        lines.append("")

        # Trading signal
        signal_icon = {"BUY": "🔵", "SELL": "🔴", "HOLD": "⚪"}.get(signal, "⚪")
        lines.append(f"{signal_icon} SIGNAL: {signal}")
        lines.append(f"  Reason: {signal_reason}")
        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
