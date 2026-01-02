"""
Main flow state monitor module.

This module integrates borrow-rate dynamics and price behavior analysis to
detect market flow states driven by forced buying pressure.
"""

from typing import Dict, List, Optional
from .config import Config
from .borrow_level import detect_borrow_level
from .borrow_delta import detect_borrow_delta
from .borrow_momentum import detect_borrow_momentum
from .price_behavior import detect_price_spike, detect_abnormal_volatility


class FlowStateMonitor:
    """
    Monitor market flow states driven by forced buying pressure.
    
    This class analyzes borrow-rate dynamics (level, delta, momentum) and
    price behavior to detect when forced buying pressure from short covering
    is active, weakening, or gone.
    
    Flow states:
        - ON: Forced buying pressure is active (high borrow rates, rising, price spikes)
        - WEAKENING: Pressure exists but is diminishing (high rates but falling)
        - OFF: No significant forced buying pressure detected
    
    This is NOT a trading signal or prediction tool. It monitors observable
    flow states to support disciplined exit decisions.
    
    Attributes:
        config: Configuration object containing detection parameters
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the flow state monitor.
        
        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or Config()
    
    def analyze(
        self,
        borrow_rates: List[float],
        prices: List[float]
    ) -> Dict:
        """
        Analyze market data to detect flow state.
        
        Args:
            borrow_rates: List of daily borrow rates in percent (most recent last)
            prices: List of daily closing prices (most recent last)
            
        Returns:
            Dictionary containing:
                - flow_state: Overall flow state ("ON", "WEAKENING", "OFF")
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
        
        # Analyze borrow rate momentum
        try:
            momentum_config = self.config.get_section("borrow_momentum")
            lookback = momentum_config["lookback_period"]
            # Use available data if less than lookback period
            momentum_data = borrow_rates[-min(lookback+1, len(borrow_rates)):]
            
            momentum_type, momentum_details = detect_borrow_momentum(
                momentum_data,
                positive_threshold=momentum_config["positive_threshold_pct_points"],
                negative_threshold=momentum_config["negative_threshold_pct_points"]
            )
            signals["borrow_momentum"] = {
                "momentum_type": momentum_type,
                "details": momentum_details
            }
        except Exception as e:
            signals["borrow_momentum"] = {
                "momentum_type": "UNKNOWN",
                "error": str(e)
            }
        
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
        
        # Generate summary
        summary = self._generate_summary(flow_state, signals)
        
        return {
            "flow_state": flow_state,
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
    
    def _generate_summary(self, flow_state: str, signals: Dict) -> str:
        """
        Generate human-readable summary of flow state.
        
        Args:
            flow_state: Determined flow state
            signals: Dictionary of individual signal results
            
        Returns:
            Summary string
        """
        borrow_level = signals.get("borrow_level", {}).get("level", "UNKNOWN")
        borrow_rate = signals.get("borrow_level", {}).get("details", {}).get("borrow_rate", 0)
        
        if flow_state == "ON":
            return (
                f"⚠️  FLOW STATE: ON - Forced buying pressure is ACTIVE. "
                f"Borrow rate: {borrow_rate:.1f}% ({borrow_level}). "
                f"Pressure indicators suggest ongoing short covering activity."
            )
        elif flow_state == "WEAKENING":
            return (
                f"⚡ FLOW STATE: WEAKENING - Forced buying pressure is DIMINISHING. "
                f"Borrow rate: {borrow_rate:.1f}% ({borrow_level}). "
                f"Pressure indicators suggest short covering is slowing down."
            )
        else:
            return (
                f"✓ FLOW STATE: OFF - No significant forced buying pressure detected. "
                f"Borrow rate: {borrow_rate:.1f}% ({borrow_level}). "
                f"Market flow appears normal."
            )
