"""
Example: Relative Strength Analysis

This example demonstrates the automatic relative strength comparison
against SPY and QQQ benchmarks when using live data sources.
"""

# When using live data (IBKR Borrow Sensor + Alpaca/IBKR), relative strength is automatic!
# Just run the command and you'll get:
# 1. Flow state analysis (ON/OFF/WEAKENING)
# 2. Relative strength vs SPY (S&P 500)
# 3. Relative strength vs QQQ (Nasdaq-100)
# 4. Warnings if signals conflict

# Example 1: Stock outperforming benchmarks (strong signal)
# flow-state-monitor INTL
# Output shows:
# - Flow State: ON
# - INTL: +1.51%
# - vs SPY: outperforming by +1.06%
# - vs QQQ: outperforming by +2.19%
# ✓ No warnings - flow ON and stock performing well

# Example 2: Stock underperforming benchmarks (weak signal)
# flow-state-monitor AAPL
# Output shows:
# - Flow State: ON
# - AAPL: -4.29%
# - vs SPY: underperforming by -4.75%
# - vs QQQ: underperforming by -3.62%
# ⚠️ WARNING: Flow is ON but stock underperforming
#    This may indicate a weak or false signal

# Example 3: Programmatic usage
import os

from flow_state_monitor import FlowStateMonitor
from flow_state_monitor.alpaca_data import fetch_combined_data
from flow_state_monitor.market_context import MarketContextAnalyzer

# Set up credentials
snapshot_dir = os.getenv('IBKR_SNAPSHOT_DIR', './output')
alpaca_key = os.getenv('ALPACA_API_KEY')
alpaca_secret = os.getenv('ALPACA_SECRET_KEY')

if alpaca_key and alpaca_secret:
    # Fetch stock data
    data = fetch_combined_data(
        symbol='AAPL',
        days=25,
        ibkr_snapshot_dir=snapshot_dir,
        alpaca_api_key=alpaca_key,
        alpaca_secret_key=alpaca_secret,
        paper=True
    )

    # Analyze flow state
    monitor = FlowStateMonitor()
    results = monitor.analyze(**data)

    print(f"Flow State: {results['flow_state']}")

    # Fetch benchmark data for relative strength
    from flow_state_monitor.alpaca_data import AlpacaDataFetcher

    analyzer = MarketContextAnalyzer()

    with AlpacaDataFetcher(api_key=alpaca_key, secret_key=alpaca_secret, paper=True) as fetcher:
        benchmark_prices = analyzer.get_benchmark_prices(fetcher, days=25)

    # Calculate relative strength
    relative_strength = analyzer.analyze_relative_strength(
        symbol='AAPL',
        stock_prices=data['prices'],
        benchmark_prices=benchmark_prices
    )

    print("\nRelative Strength:")
    print(relative_strength.description)

    # Check for warning conditions
    if results['flow_state'] == 'ON' and not relative_strength.outperforming_spy:
        print("\n⚠️ WARNING: Flow is ON but stock underperforming SPY")
        print("   Consider this a potentially weak signal")
    else:
        print("\n✓ Flow and relative strength align")
else:
    print("Set ALPACA_API_KEY and ALPACA_SECRET_KEY to run this example")
    print("Get free keys at: https://alpaca.markets/")
