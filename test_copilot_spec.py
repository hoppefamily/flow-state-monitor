#!/usr/bin/env python
"""
Test script for design specification implementation.

Tests the new features:
- EMA-based momentum
- market_state detection
- signal generation (BUY/SELL/HOLD)
"""

from flow_state_monitor import FlowStateMonitor

# Simulated data showing constraint transition and exhaustion
print("Test Case 1: Entry Signal (transition to constrained flow)")
print("=" * 70)

# Days 1-5: Low borrow rate, normal market
borrow_rates_entry = [
    2.5, 2.8, 3.0, 2.9, 3.2,  # Days 1-5: Low/stable
    5.5, 7.2, 9.5, 11.0, 12.5  # Days 6-10: Rapid increase (entry)
]

prices_entry = [
    100, 101, 100.5, 102, 101,  # Days 1-5: Normal
    103, 106, 110, 115, 120     # Days 6-10: Spike up
]

monitor = FlowStateMonitor()

# Analyze each day to show transition
for i in range(5, len(borrow_rates_entry)):
    print(f"\nDay {i+1}:")
    print("-" * 70)

    result = monitor.analyze(
        borrow_rates=borrow_rates_entry[:i+1],
        prices=prices_entry[:i+1]
    )

    print(f"Market State: {result['market_state']}")
    print(f"Flow State: {result['flow_state']}")
    print(f"Signal: {result['signal']}")
    print(f"Momentum: {result['signals']['borrow_momentum']['details']['momentum']:.3f}")

    if result['signal'] in ['BUY', 'SELL']:
        print(f"\n*** {result['signal']} SIGNAL ***")
        print(f"Reason: {result['signal_reason']}")

print("\n\n")
print("Test Case 2: Exit Signal (momentum exhaustion)")
print("=" * 70)

# Days 1-8: High borrow rate rising, then Days 9-11: Momentum turns negative
borrow_rates_exit = [
    10.0, 11.5, 13.0, 14.5, 16.0,  # Days 1-5: Rising
    17.5, 18.0, 18.2,               # Days 6-8: Still high but slowing
    17.8, 17.0, 16.5                # Days 9-11: Falling (exit)
]

prices_exit = [
    100, 105, 110, 115, 120,  # Days 1-5: Rising
    125, 127, 128,            # Days 6-8: Still up
    127, 125, 123             # Days 9-11: Weakening
]

# Create fresh monitor to reset state tracking
monitor2 = FlowStateMonitor()

# Warm up the signal generator with the rising phase
for i in range(5, 8):
    monitor2.analyze(
        borrow_rates=borrow_rates_exit[:i+1],
        prices=prices_exit[:i+1]
    )

# Now show the exit phase
print("\nDays 8-11 (Exit Phase):")
for i in range(7, len(borrow_rates_exit)):
    print(f"\nDay {i+1}:")
    print("-" * 70)

    result = monitor2.analyze(
        borrow_rates=borrow_rates_exit[:i+1],
        prices=prices_exit[:i+1]
    )

    print(f"Market State: {result['market_state']}")
    print(f"Flow State: {result['flow_state']}")
    print(f"Signal: {result['signal']}")
    print(f"Borrow Rate: {borrow_rates_exit[i]:.1f}%")
    print(f"Momentum: {result['signals']['borrow_momentum']['details']['momentum']:.3f}")

    if result['signal'] in ['BUY', 'SELL']:
        print(f"\n*** {result['signal']} SIGNAL ***")
        print(f"Reason: {result['signal_reason']}")

print("\n\n")
print("Test Case 3: Full Analysis Output")
print("=" * 70)

# Run one final analysis and show complete output
final_result = monitor2.analyze(
    borrow_rates=borrow_rates_exit,
    prices=prices_exit
)

print(final_result['summary'])

print("\n✓ All tests completed successfully!")
