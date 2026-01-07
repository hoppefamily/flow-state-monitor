"""
Example: Using IBKR Borrow Sensor for borrow rate data

This example demonstrates how to fetch borrow rate data from IBKR Borrow Sensor
snapshot files and analyze it with flow-state-monitor.

Prerequisites:
1. IBKR Borrow Sensor must be installed and running in a separate project
2. Snapshot files must exist in the output directory (e.g., ./output/borrow-state-AAPL-latest.json)

Repository: https://github.com/hoppefamily/ibkr-borrow-sensor
"""

from flow_state_monitor import FlowStateMonitor
from flow_state_monitor.ibkr_borrow_data import fetch_ibkr_borrow_rates

# Configuration
SYMBOL = 'AAPL'
DAYS = 30
SNAPSHOT_DIR = './output'  # Path to IBKR Borrow Sensor snapshots

def main():
    print(f"Fetching {DAYS} days of borrow rate data for {SYMBOL}...")
    print(f"Reading from snapshot directory: {SNAPSHOT_DIR}\n")
    
    # Fetch borrow rates from IBKR Borrow Sensor snapshots
    try:
        borrow_data = fetch_ibkr_borrow_rates(
            symbol=SYMBOL,
            days=DAYS,
            snapshot_dir=SNAPSHOT_DIR
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. IBKR Borrow Sensor is installed and has run at least once")
        print(f"2. Snapshot file exists: {SNAPSHOT_DIR}/borrow-state-{SYMBOL}-latest.json")
        print("3. The snapshot directory path is correct")
        return
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    
    print(f"✓ Successfully fetched {len(borrow_data['borrow_rates'])} days of borrow rate data")
    print(f"  Current rate: {borrow_data['borrow_rates'][-1]:.2f}%")
    print(f"  Average rate: {sum(borrow_data['borrow_rates']) / len(borrow_data['borrow_rates']):.2f}%\n")
    
    # Example: Combine with your own price data
    # In a real application, you'd fetch actual price data from your data source
    # Here we'll use dummy data for demonstration
    print("Note: You need to provide price data from another source")
    print("      (e.g., Alpaca, IBKR, CSV file, etc.)\n")
    
    # Dummy price data for demonstration
    # Replace this with actual price data in your application
    dummy_prices = [100 + i * 0.5 for i in range(DAYS)]
    
    # Analyze with flow-state-monitor
    monitor = FlowStateMonitor()
    results = monitor.analyze(
        borrow_rates=borrow_data['borrow_rates'],
        prices=dummy_prices
    )
    
    # Print results
    print("=" * 60)
    print("FLOW STATE ANALYSIS")
    print("=" * 60)
    print(f"Flow State: {results['flow_state']}")
    print(f"Summary: {results['summary']}")
    print("=" * 60)


if __name__ == '__main__':
    main()
