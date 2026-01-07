"""
Example: Using Alpaca Markets data with flow state monitor.

This example demonstrates how to fetch price data from Alpaca Markets
and combine it with IBKR Borrow Sensor borrow rate data for complete flow state analysis.

Prerequisites:
    1. Install alpaca-py: pip install alpaca-py
    2. Sign up for free Alpaca account at https://alpaca.markets/
    3. Get your API keys from the Alpaca dashboard
    4. Set environment variables or pass keys directly:
       export ALPACA_API_KEY="your_api_key"
       export ALPACA_SECRET_KEY="your_secret_key"
       export IBKR_SNAPSHOT_DIR="./output"

Note: Alpaca only supports US equities. No forex, futures, or international stocks.
"""

import os

from flow_state_monitor import FlowStateMonitor

try:
    from flow_state_monitor.alpaca_data import (
        AlpacaDataFetcher,
        fetch_alpaca_prices,
        fetch_combined_data,
    )
except ImportError:
    print("ERROR: alpaca-py library is not installed.")
    print("Install with: pip install alpaca-py")
    exit(1)


def example_simple_fetch():
    """
    Simple example: Fetch price data from Alpaca.
    """
    print("=" * 70)
    print("EXAMPLE 1: Simple Alpaca Price Data Fetch")
    print("=" * 70)

    try:
        # Fetch price data using convenience function
        print("\nFetching 30 days of AAPL price data from Alpaca...")
        data = fetch_alpaca_prices(
            symbol='AAPL',
            days=30,
            paper=True  # Paper trading (default)
        )

        print(f"Retrieved {len(data['prices'])} daily prices")
        print(f"Price range: ${data['prices'][0]:.2f} -> ${data['prices'][-1]:.2f}")

    except ValueError as e:
        print(f"Error: {e}")
        return


def example_complete_solution():
    """
    Complete solution: Fetch both borrow rates from IBKR Borrow Sensor and prices from Alpaca.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Complete Solution - IBKR Borrow Sensor + Alpaca")
    print("=" * 70)

    try:
        # Fetch everything from APIs
        print("\nFetching data for AAPL from IBKR Borrow Sensor and Alpaca...")
        data = fetch_combined_data(
            symbol='AAPL',
            days=30,
            paper=True
        )

        print(f"Retrieved {len(data['borrow_rates'])} days of data")
        print(f"Borrow rate range: {data['borrow_rates'][0]:.2f}% -> {data['borrow_rates'][-1]:.2f}%")
        print(f"Price range: ${data['prices'][0]:.2f} -> ${data['prices'][-1]:.2f}")

        # Analyze flow state
        print("\nAnalyzing flow state...")
        monitor = FlowStateMonitor()
        results = monitor.analyze(**data)

        print("\n" + results['summary'])

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set IBKR_SNAPSHOT_DIR, ALPACA_API_KEY,")
        print("and ALPACA_SECRET_KEY environment variables.")


def example_with_fetcher_class():
    """
    Using AlpacaDataFetcher class directly for more control.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Using AlpacaDataFetcher Class")
    print("=" * 70)

    try:
        # Create fetcher with explicit credentials
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')

        with AlpacaDataFetcher(api_key=api_key, secret_key=secret_key) as fetcher:
            print("\nFetching AAPL price data...")
            aapl_data = fetcher.fetch_daily_bars('AAPL', days=30)
            print(f"AAPL: {len(aapl_data['prices'])} bars")

            print("\nFetching MSFT price data...")
            msft_data = fetcher.fetch_daily_bars('MSFT', days=30)
            print(f"MSFT: {len(msft_data['prices'])} bars")

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run examples
    example_simple_fetch()
    example_complete_solution()
    example_with_fetcher_class()

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
