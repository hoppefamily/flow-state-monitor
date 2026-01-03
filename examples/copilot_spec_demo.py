#!/usr/bin/env python
"""
Comprehensive demonstration of the design specification implementation.

This example shows:
1. Market state detection (elastic vs constrained)
2. Flow state detection (forced buying pressure)
3. BUY signal on state transitions
4. SELL signal on momentum exhaustion
5. EMA-based momentum calculation
"""

from flow_state_monitor import FlowStateMonitor

print("=" * 70)
print("DESIGN SPECIFICATION IMPLEMENTATION DEMONSTRATION")
print("=" * 70)
print()

# Simulate a complete flow cycle
# Phase 1 (Days 1-7): Normal market
# Phase 2 (Days 8-9): Rapid transition to constrained (ENTRY)
# Phase 3 (Days 10-14): High tension sustained
# Phase 4 (Days 15-17): Momentum exhaustion (EXIT)

borrow_rates = [
    # Phase 1: Normal (market_state=OFF, flow_state=OFF)
    2.0, 2.5, 3.0, 2.8, 3.2, 2.9, 3.1,

    # Phase 2: Rapid spike (ENTRY - both states flip ON)
    6.5, 11.0,

    # Phase 3: High and rising (flow continues)
    13.5, 15.0, 16.5, 17.2, 18.0,

    # Phase 4: Momentum turns negative (EXIT)
    17.5, 16.8, 16.0
]

prices = [
    # Phase 1: Normal
    100, 101, 100, 102, 101, 103, 102,

    # Phase 2: Spike
    107, 115,

    # Phase 3: Continued rise
    120, 125, 130, 133, 135,

    # Phase 4: Stalling
    134, 132, 130
]

monitor = FlowStateMonitor()

# Key days to show
key_days = [7, 8, 9, 14, 15, 16]

for day_idx in key_days:
    if day_idx < 6:  # Need at least 6 data points
        continue

    result = monitor.analyze(
        borrow_rates=borrow_rates[:day_idx+1],
        prices=prices[:day_idx+1]
    )

    print(f"Day {day_idx+1}")
    print("-" * 70)
    print(f"Borrow Rate: {borrow_rates[day_idx]:.1f}%")
    print(f"Price: ${prices[day_idx]:.0f}")
    print()

    # Show key metrics
    momentum = result['signals']['borrow_momentum']['details']['momentum']
    delta = result['signals']['borrow_delta']['details']['delta']

    print(f"Market State: {result['market_state']}")
    print(f"Flow State: {result['flow_state']}")
    print(f"Delta: {delta:+.2f} pct pts")
    print(f"Momentum (EMA-3): {momentum:+.3f} pct pts/day")
    print()

    signal = result['signal']
    if signal == 'BUY':
        print("🔵 " + "=" * 66)
        print("   BUY SIGNAL TRIGGERED")
        print("   " + result['signal_reason'])
        print("=" * 68)
    elif signal == 'SELL':
        print("🔴 " + "=" * 66)
        print("   SELL SIGNAL TRIGGERED")
        print("   " + result['signal_reason'])
        print("=" * 68)
    else:
        print(f"Signal: {signal} - {result['signal_reason']}")

    print()

print()
print("=" * 70)
print("KEY OBSERVATIONS:")
print("=" * 70)
print()
print("1. ENTRY (BUY): Triggered when both market_state and flow_state")
print("   transitioned from OFF to ON (Day 8-9)")
print()
print("2. EXIT (SELL): Triggered when EMA(ΔB) < -epsilon for 1+ day")
print("   (Day 16-17 when momentum turned negative)")
print()
print("3. MOMENTUM: Uses EMA smoothing of daily deltas (span=3)")
print("   to filter noise and detect true constraint exhaustion")
print()
print("4. DETERMINISTIC: All thresholds configurable, no ML/prediction")
print()
print("=" * 70)
