#!/usr/bin/env python
"""
Test BUY signal with proper state transition.
"""

from flow_state_monitor import FlowStateMonitor

print("Test: BUY Signal on State Transition")
print("=" * 70)

# Scenario: Stock goes from normal to constrained in 2 days
# Day 1-6: Normal market (borrow rate < 5%)
# Day 7-8: Rapid transition to forced flow
borrow_rates = [
    2.0, 2.5, 3.0, 2.8, 3.2, 2.9,  # Days 1-6: Low, market_state=OFF, flow_state=OFF
    6.5, 9.0                        # Days 7-8: Spike up, both states flip to ON
]

prices = [
    100, 101, 100, 102, 101, 103,  # Days 1-6: Normal
    107, 115                        # Days 7-8: Spike up
]

monitor = FlowStateMonitor()

# Analyze day by day
for i in range(5, len(borrow_rates)):
    print(f"\nDay {i+1}:")
    print("-" * 70)

    result = monitor.analyze(
        borrow_rates=borrow_rates[:i+1],
        prices=prices[:i+1]
    )

    print(f"Market State: {result['market_state']}")
    print(f"Flow State: {result['flow_state']}")
    print(f"Borrow Rate: {borrow_rates[i]:.1f}%")
    print(f"Signal: {result['signal']}")

    if result['signal'] in ['BUY', 'SELL']:
        print(f"\n*** {result['signal']} SIGNAL ***")
        print(f"Reason: {result['signal_reason']}")
        print()
        print(result['summary'])

print("\n\n✓ Test completed!")
