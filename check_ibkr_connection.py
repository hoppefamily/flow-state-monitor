#!/usr/bin/env python3
"""
Quick script to check IBKR/CapTrader connection for flow-state-monitor.

This script verifies that:
1. ib_insync is installed
2. TWS or IB Gateway is running
3. API connection is working
4. Price data can be fetched

Run this after setting up IBKR integration to verify everything works.
"""

import sys


def check_ib_insync():
    """Check if ib_insync is installed."""
    print("=" * 70)
    print("1. Checking ib_insync installation...")
    print("=" * 70)

    try:
        import ib_insync
        version = getattr(ib_insync, '__version__', 'unknown')
        print(f"✓ ib_insync is installed (version: {version})")
        return True
    except ImportError:
        print("✗ ib_insync is NOT installed")
        print("\nInstall with: pip install ib_insync")
        return False


def check_connection(port=7497):
    """Check if we can connect to IBKR."""
    print("\n" + "=" * 70)
    print(f"2. Testing connection to IBKR on port {port}...")
    print("=" * 70)

    try:
        from flow_state_monitor.ibkr_data import IBKRDataFetcher

        print(f"Attempting connection to 127.0.0.1:{port}...")
        fetcher = IBKRDataFetcher(port=port)
        fetcher.connect(timeout=5)

        if fetcher.is_connected():
            print("✓ Successfully connected to IBKR")
            fetcher.disconnect()
            return True
        else:
            print("✗ Connection established but status check failed")
            return False

    except ConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure TWS or IB Gateway is running")
        print("2. Check that you're logged in to your IBKR account")
        print("3. Enable API in: File → Global Configuration → API → Settings")
        print("4. Check 'Enable ActiveX and Socket Clients'")
        print(f"5. Verify port {port} is correct:")
        print("   - 7497 = TWS paper trading")
        print("   - 7496 = TWS live trading")
        print("   - 4002 = IB Gateway paper trading")
        print("   - 4001 = IB Gateway live trading")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def check_data_fetch(port=7497):
    """Check if we can fetch sample data."""
    print("\n" + "=" * 70)
    print("3. Testing data fetch...")
    print("=" * 70)

    try:
        from flow_state_monitor.ibkr_data import fetch_ibkr_data

        print("Fetching 5 days of AAPL price data...")
        data = fetch_ibkr_data('AAPL', days=5, port=port)

        if 'prices' in data and len(data['prices']) > 0:
            print(f"✓ Successfully fetched {len(data['prices'])} days of data")
            print(f"  Price range: ${min(data['prices']):.2f} - ${max(data['prices']):.2f}")
            print(f"  Latest close: ${data['prices'][-1]:.2f}")
            return True
        else:
            print("✗ Data fetch returned empty result")
            return False

    except Exception as e:
        print(f"✗ Data fetch failed: {e}")
        return False


def main():
    """Run all checks."""
    print("\n" + "=" * 70)
    print("IBKR CONNECTION CHECK FOR FLOW-STATE-MONITOR")
    print("=" * 70)
    print("\nThis script will verify your IBKR integration is working correctly.")
    print("Make sure TWS or IB Gateway is running before continuing.\n")

    # Check for custom port
    port = 7497  # Default paper trading port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            print(f"Using custom port: {port}\n")
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            print("Usage: python check_ibkr_connection.py [port]")
            sys.exit(1)

    # Run checks
    results = []
    results.append(check_ib_insync())

    if results[0]:  # Only proceed if ib_insync is installed
        results.append(check_connection(port))

        if results[1]:  # Only proceed if connection works
            results.append(check_data_fetch(port))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if all(results):
        print("\n✓ All checks passed! IBKR integration is working correctly.")
        print("\nYou can now use IBKR with flow-state-monitor:")
        print("  Python: from flow_state_monitor.ibkr_data import fetch_ibkr_data")
        print("  CLI:    flow-state-monitor --ibkr SYMBOL --borrow-csv rates.csv")
        print("\nNote: IBKR only provides price data. Borrow rates must come from")
        print("      another source (broker API, data vendor, or manual tracking).")
        return 0
    else:
        print("\n✗ Some checks failed. See above for troubleshooting steps.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
