"""
Example: Using Ortex API to fetch borrow rate data for flow state monitoring.

This example demonstrates how to fetch borrow rate data from Ortex API
and combine it with price data for comprehensive flow state analysis.

Prerequisites:
    1. Ortex API key (use 'TEST' for demo access)
    2. Sign up at: https://public.ortex.com/

Note: Ortex provides borrow rates and short interest data.
      For complete analysis, combine with price data from IBKR or CSV.
"""

from flow_state_monitor import FlowStateMonitor

try:
    from flow_state_monitor.ortex_data import (
        OrtexDataFetcher,
        fetch_combined_data,
        fetch_ortex_borrow_rates,
    )
except ImportError as e:
    print(f"ERROR: {e}")
    exit(1)


def example_simple_fetch():
    """
    Simple example: Fetch borrow rates from Ortex.
    """
    print("=" * 70)
    print("EXAMPLE 1: Simple Ortex Borrow Rate Fetch")
    print("=" * 70)

    try:
        # Fetch borrow rates using convenience function with TEST key
        print("\nFetching 30 days of AAPL borrow rates from Ortex (demo)...")
        data = fetch_ortex_borrow_rates(
            symbol='AAPL',
            days=30,
            api_key='TEST'  # Use demo key
        )

        print(f"Successfully fetched {len(data['borrow_rates'])} days of borrow rate data")
        print(f"Borrow rate range: {min(data['borrow_rates']):.2f}% - {max(data['borrow_rates']):.2f}%")
        print(f"Latest borrow rate: {data['borrow_rates'][-1]:.2f}%")

        # For complete analysis, you need price data
        print("\nNote: You need price data from IBKR or CSV for complete analysis")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Demo key 'TEST' has limited data. Use your API key for real data.")


def example_with_prices():
    """
    Example: Combine Ortex borrow rates with simulated prices.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Complete Analysis with Borrow Rates and Prices")
    print("=" * 70)

    try:
        # Fetch borrow rates from Ortex
        print("\nFetching AAPL borrow rates from Ortex...")
        borrow_data = fetch_ortex_borrow_rates('AAPL', days=20, api_key='TEST')

        print(f"Fetched {len(borrow_data['borrow_rates'])} days of borrow rates")

        # In practice, fetch prices from IBKR or load from CSV
        # For this example, simulate some price data
        print("\nNote: Using simulated price data for demonstration")
        num_days = len(borrow_data['borrow_rates'])

        # Simulated prices that align with borrow rates
        base_price = 150.0
        prices = [base_price + (i * 2.5) for i in range(num_days)]

        # Analyze with monitor
        monitor = FlowStateMonitor()
        results = monitor.analyze(
            borrow_rates=borrow_data['borrow_rates'],
            prices=prices
        )

        print(f"\n{results['summary']}")
        print(f"Flow State: {results['flow_state']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_ortex_and_ibkr():
    """
    Example: Fetch both borrow rates (Ortex) and prices (IBKR).

    Note: Requires TWS/Gateway running for IBKR connection.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Complete Solution - Ortex + IBKR")
    print("=" * 70)
    print("\nThis example requires TWS/IB Gateway running.")
    print("Skipping if IBKR is not available...\n")

    try:
        # This will fetch both borrow rates and prices
        print("Fetching AAPL data from Ortex (borrow) and IBKR (prices)...")

        data = fetch_combined_data(
            symbol='AAPL',
            days=20,
            ortex_api_key='TEST',  # Use your real key
            ibkr_port=7497  # Paper trading port
        )

        print(f"Successfully fetched {len(data['borrow_rates'])} days of combined data")
        print(f"Borrow rates: {min(data['borrow_rates']):.2f}% - {max(data['borrow_rates']):.2f}%")
        print(f"Prices: ${min(data['prices']):.2f} - ${max(data['prices']):.2f}")

        # Analyze
        monitor = FlowStateMonitor()
        results = monitor.analyze(**data)

        print(f"\nFlow State: {results['flow_state']}")
        print(f"{results['summary']}")

    except ImportError:
        print("❌ IBKR integration not available (ib_insync not installed)")
    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("\nMake sure TWS or IB Gateway is running")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_with_fetcher_class():
    """
    Example: Using OrtexDataFetcher class directly.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Using OrtexDataFetcher Class")
    print("=" * 70)

    try:
        # Create fetcher with API key
        fetcher = OrtexDataFetcher(api_key='TEST')

        # Fetch borrow rates
        print("\nFetching TSLA borrow rates...")
        data = fetcher.fetch_borrow_rates('TSLA', days=15)

        print(f"Fetched {len(data['borrow_rates'])} days")
        print(f"Latest borrow rate: {data['borrow_rates'][-1]:.2f}%")

        # You can also fetch comprehensive short interest data
        # print("\nFetching comprehensive short interest data...")
        # short_data = fetcher.fetch_short_interest('TSLA', days=15)
        # This returns more detailed metrics

    except Exception as e:
        print(f"❌ Error: {e}")


def example_multiple_symbols():
    """
    Example: Fetch borrow rates for multiple symbols.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Multiple Symbols")
    print("=" * 70)

    symbols = ['AAPL', 'TSLA', 'GME']
    fetcher = OrtexDataFetcher(api_key='TEST')

    print(f"\nFetching borrow rates for {len(symbols)} symbols...")

    for symbol in symbols:
        try:
            data = fetcher.fetch_borrow_rates(symbol, days=10)
            latest_rate = data['borrow_rates'][-1]
            print(f"{symbol}: {latest_rate:.2f}% (latest borrow rate)")
        except Exception as e:
            print(f"{symbol}: Failed - {e}")


def example_with_real_api_key():
    """
    Template for using your real Ortex API key.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Template for Real API Key")
    print("=" * 70)

    print("""
To use your real Ortex API key:

1. Sign up at https://public.ortex.com/
2. Get your API key from account settings
3. Replace 'YOUR_API_KEY' below:

    from flow_state_monitor.ortex_data import fetch_combined_data
    from flow_state_monitor import FlowStateMonitor

    # Fetch both borrow and price data
    data = fetch_combined_data(
        symbol='AAPL',
        days=30,
        ortex_api_key='YOUR_API_KEY',  # Your real key here
        ibkr_port=7497
    )

    # Analyze
    monitor = FlowStateMonitor()
    results = monitor.analyze(**data)
    print(results['summary'])

Or via CLI:
    flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --ibkr AAPL --days 30
    """)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FLOW STATE MONITOR - ORTEX INTEGRATION EXAMPLES")
    print("=" * 70)
    print("\nThese examples use the 'TEST' API key for demonstration.")
    print("For real data, sign up at https://public.ortex.com/")
    print("=" * 70)

    # Run examples
    example_simple_fetch()
    example_with_prices()
    example_ortex_and_ibkr()
    example_with_fetcher_class()
    example_multiple_symbols()
    example_with_real_api_key()

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
