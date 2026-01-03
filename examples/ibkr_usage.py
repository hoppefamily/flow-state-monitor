"""
Example: Using IBKR/CapTrader data with the flow state monitor.

This example demonstrates how to fetch daily price data from Interactive Brokers
or CapTrader and combine it with borrow rate data for flow state analysis.

Prerequisites:
    1. Install ib_insync: pip install ib_insync
    2. Have TWS (Trader Workstation) or IB Gateway running
    3. Enable API connections in TWS/Gateway settings:
       - Go to File -> Global Configuration -> API -> Settings
       - Check "Enable ActiveX and Socket Clients"
       - Set a port (7497 for paper trading, 7496 for live)
       - Add 127.0.0.1 to trusted IPs if needed

Note: IBKR only provides price data. Borrow rates must come from another source
      such as your broker's API, a data vendor, or manual tracking.
"""

from flow_state_monitor import FlowStateMonitor

try:
    from flow_state_monitor.ibkr_data import IBKRDataFetcher, fetch_ibkr_data
except ImportError:
    print("ERROR: ib_insync library is not installed.")
    print("Install with: pip install ib_insync")
    exit(1)


def example_simple_fetch():
    """
    Simple example: Fetch price data and combine with borrow rates.
    """
    print("=" * 70)
    print("EXAMPLE 1: Simple IBKR Data Fetch")
    print("=" * 70)

    try:
        # Fetch price data using convenience function
        # This automatically connects and disconnects
        print("\nFetching 30 days of AAPL price data from IBKR...")
        data = fetch_ibkr_data(
            symbol='AAPL',
            days=30,
            port=7497  # Paper trading port
        )

        print(f"Successfully fetched {len(data['prices'])} days of price data")
        print(f"Price range: ${min(data['prices']):.2f} - ${max(data['prices']):.2f}")

        # In practice, you would get borrow rates from your data provider
        # For this example, we'll simulate some borrow rate data
        print("\nNote: You need to provide borrow rates from your data source")
        print("For this example, using simulated borrow rate data...")

        # Simulated borrow rates that align with the price data
        # In practice, get this from your broker or data provider
        num_days = len(data['prices'])
        borrow_rates = [2.5 + (i * 0.8) for i in range(num_days)]  # Simulated rising rates

        # Analyze with monitor
        monitor = FlowStateMonitor()
        results = monitor.analyze(
            borrow_rates=borrow_rates,
            prices=data['prices']
        )

        print(f"\n{results['summary']}")
        print(f"Flow State: {results['flow_state']}")

    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure TWS or IB Gateway is running")
        print("2. Check that API connections are enabled")
        print("3. Verify the port number (7497 for paper, 7496 for live)")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_context_manager():
    """
    Example using context manager for persistent connection.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Using Context Manager")
    print("=" * 70)

    try:
        # Use context manager for automatic connection handling
        with IBKRDataFetcher(host='127.0.0.1', port=7497, client_id=1) as fetcher:
            print("\nConnected to IBKR")

            # Fetch data for a single symbol
            print("Fetching AAPL data...")
            aapl_data = fetcher.fetch_daily_bars('AAPL', days=30)

            print(f"AAPL: {len(aapl_data['prices'])} days")
            print(f"  Latest close: ${aapl_data['prices'][-1]:.2f}")

            # You could fetch multiple symbols efficiently
            print("\nFetching data for multiple symbols...")
            symbols_data = fetcher.fetch_multiple_symbols(['MSFT', 'GOOGL'], days=30)

            for symbol, data in symbols_data.items():
                if data:
                    print(f"{symbol}: Latest close: ${data['prices'][-1]:.2f}")

        print("\nDisconnected from IBKR")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_manual_connection():
    """
    Example with manual connection management.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Manual Connection Management")
    print("=" * 70)

    fetcher = IBKRDataFetcher(host='127.0.0.1', port=7497, client_id=1)

    try:
        # Connect manually
        print("\nConnecting to IBKR...")
        fetcher.connect(timeout=10)
        print("Connected successfully")

        # Check connection status
        if fetcher.is_connected():
            print("Connection status: Active")

            # Fetch data
            print("\nFetching 20 days of SPY data...")
            spy_data = fetcher.fetch_daily_bars(
                symbol='SPY',
                days=20,
                exchange='ARCA'  # Specify exchange
            )

            print(f"Fetched {len(spy_data['prices'])} days")
            print(f"Latest close: ${spy_data['prices'][-1]:.2f}")

            # Simulate borrow rates for analysis
            borrow_rates = [1.5 + (i * 0.3) for i in range(len(spy_data['prices']))]

            # Analyze
            monitor = FlowStateMonitor()
            results = monitor.analyze(
                borrow_rates=borrow_rates,
                prices=spy_data['prices']
            )

            print(f"\nFlow State: {results['flow_state']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Always disconnect
        print("\nDisconnecting...")
        fetcher.disconnect()
        print("Disconnected")


def example_with_config():
    """
    Example using custom configuration.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom Configuration")
    print("=" * 70)

    try:
        from flow_state_monitor import Config

        # Create custom config
        config = Config()  # Or load from file: Config('custom_config.yaml')

        # Fetch data
        print("\nFetching TSLA data from IBKR...")
        data = fetch_ibkr_data('TSLA', days=30, port=7497)

        # Simulated borrow rates
        borrow_rates = [5.0 + (i * 0.5) for i in range(len(data['prices']))]

        # Analyze with custom config
        monitor = FlowStateMonitor(config)
        results = monitor.analyze(
            borrow_rates=borrow_rates,
            prices=data['prices']
        )

        print(f"\n{results['summary']}")

        # Check specific signals
        if 'borrow_level' in results['signals']:
            level = results['signals']['borrow_level']
            print(f"\nBorrow Level: {level['level']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FLOW STATE MONITOR - IBKR INTEGRATION EXAMPLES")
    print("=" * 70)
    print("\nIMPORTANT: Make sure TWS or IB Gateway is running before running these examples")
    print("=" * 70)

    # Run examples
    example_simple_fetch()
    example_context_manager()
    example_manual_connection()
    example_with_config()

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
