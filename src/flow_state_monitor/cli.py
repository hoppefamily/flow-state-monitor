"""
Command-line interface for flow state monitor.

This module provides a CLI for analyzing market data from CSV files to
detect flow states driven by forced buying pressure.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List

from . import __version__
from .config import Config
from .monitor import FlowStateMonitor


def load_csv_data(
    filepath: str,
    borrow_rate_col: str = "borrow_rate",
    price_col: str = "close",
    require_borrow_rate: bool = True,
    require_price: bool = True
) -> Dict[str, List[float]]:
    """
    Load market data from CSV file.

    Args:
        filepath: Path to CSV file
        borrow_rate_col: Column name for borrow rates
        price_col: Column name for closing prices
        require_borrow_rate: If True, require borrow_rate column (default: True)
        require_price: If True, require price column (default: True)

    Returns:
        Dictionary with borrow_rates and prices lists

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing

    Note:
        For single-column price CSVs (no header), prices are read line by line.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    data = {
        "borrow_rates": [],
        "prices": []
    }

    with open(path, 'r') as f:
        # Try to read as CSV with header first
        first_line = f.readline().strip()
        f.seek(0)

        # Check if it looks like a header or just a number
        try:
            float(first_line)
            # It's a number, treat as headerless single-column
            is_headerless = True
        except ValueError:
            # It's text, probably a header
            is_headerless = False

        if is_headerless:
            # Headerless single-column CSV - read as prices
            for line in f:
                line = line.strip()
                if line:
                    data["prices"].append(float(line))
            if require_borrow_rate:
                raise ValueError("No borrow_rate column found in headerless CSV")
        else:
            # CSV with header
            reader = csv.DictReader(f)

            for row in reader:
                if require_borrow_rate and borrow_rate_col not in row:
                    raise ValueError(f"Required column '{borrow_rate_col}' not found in CSV")
                if require_price and price_col not in row:
                    raise ValueError(f"Required column '{price_col}' not found in CSV")

                if borrow_rate_col in row:
                    data["borrow_rates"].append(float(row[borrow_rate_col]))
                if price_col in row:
                    data["prices"].append(float(row[price_col]))

    return data


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor market flow states driven by forced buying pressure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze data from CSV file
  flow-state-monitor --csv data.csv

  # Fetch borrow rates from Ortex and prices from CSV
  flow-state-monitor --ortex AAPL --days 30 --ortex-api-key YOUR_KEY --price-csv prices.csv

  # Fetch prices from IBKR and borrow rates from CSV
  flow-state-monitor --ibkr AAPL --days 30 --port 7497 --borrow-csv borrow_data.csv

  # Fetch borrow rates from Ortex and prices from IBKR (complete solution!)
  flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --ibkr AAPL --days 30 --port 7497

  # Use Ortex demo key for testing
  flow-state-monitor --ortex AAPL --ortex-api-key TEST --price-csv prices.csv

  # Use custom config file
  flow-state-monitor --csv data.csv --config custom_config.yaml

  # Get JSON output for scripting
  flow-state-monitor --csv data.csv --json

Note: This tool monitors flow states to support disciplined exits.
      It is NOT a trading signal or prediction tool.

Data Sources:
  - Ortex: Provides borrow rate data (requires API key, use 'TEST' for demo)
  - IBKR/CapTrader: Provides price data (requires TWS/Gateway running)
  - CSV: Provides any data from file
        """
    )

    parser.add_argument(
        "--csv",
        type=str,
        help="Path to CSV file containing market data"
    )

    parser.add_argument(
        "--ortex",
        type=str,
        metavar="SYMBOL",
        help="Fetch borrow rate data from Ortex for this symbol (requires API key)"
    )

    parser.add_argument(
        "--ortex-api-key",
        type=str,
        default="TEST",
        help="Ortex API key (default: TEST for demo access)"
    )

    parser.add_argument(
        "--price-csv",
        type=str,
        help="CSV file with price data (required when using --ortex without --ibkr)"
    )

    parser.add_argument(
        "--ibkr",
        type=str,
        metavar="SYMBOL",
        help="Fetch price data from IBKR for this symbol (requires ib_insync)"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days of data to fetch (default: 30)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=7497,
        help="IBKR TWS/Gateway port (7497=paper, 7496=live, 4002=Gateway paper, 4001=Gateway live)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="IBKR TWS/Gateway host address (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--client-id",
        type=int,
        default=1,
        help="IBKR client ID (default: 1)"
    )

    parser.add_argument(
        "--borrow-csv",
        type=str,
        help="CSV file with borrow rates (required when using --ibkr)"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration YAML file"
    )

    parser.add_argument(
        "--borrow-col",
        type=str,
        default="borrow_rate",
        help="Column name for borrow rates (default: borrow_rate)"
    )

    parser.add_argument(
        "--price-col",
        type=str,
        default="close",
        help="Column name for closing prices (default: close)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"flow-state-monitor {__version__}"
    )

    args = parser.parse_args()

    # Validate arguments
    has_csv = args.csv is not None
    has_ortex = args.ortex is not None
    has_ibkr = args.ibkr is not None

    # At least one data source required
    if not has_csv and not has_ortex and not has_ibkr:
        parser.error("At least one data source required: --csv, --ortex, or --ibkr")

    # CSV is standalone
    if has_csv and (has_ortex or has_ibkr):
        parser.error("Cannot combine --csv with --ortex or --ibkr (CSV provides all data)")

    # Validate Ortex requirements
    if has_ortex and not has_ibkr and not args.price_csv:
        parser.error("--price-csv is required when using --ortex without --ibkr")

    # Validate IBKR requirements
    if has_ibkr and not has_ortex and not args.borrow_csv:
        parser.error("--borrow-csv is required when using --ibkr without --ortex")

    try:
        # Load configuration
        config = Config(args.config) if args.config else Config()

        # Load data based on source
        if args.csv:
            # Load from CSV file
            data = load_csv_data(
                args.csv,
                borrow_rate_col=args.borrow_col,
                price_col=args.price_col
            )
        elif args.ortex and args.ibkr:
            # Fetch both borrow rates from Ortex and prices from IBKR
            if not args.json:
                print(f"Fetching data for {args.ortex} from Ortex and IBKR...")

            try:
                from .ortex_data import fetch_combined_data
                data = fetch_combined_data(
                    symbol=args.ortex,
                    days=args.days,
                    ortex_api_key=args.ortex_api_key,
                    ibkr_port=args.port,
                    ibkr_host=args.host,
                    ibkr_client_id=args.client_id
                )
                if not args.json:
                    print(f"Successfully fetched {len(data['borrow_rates'])} days of data")
            except Exception as e:
                if args.json:
                    print(json.dumps({"error": f"Data fetch failed: {str(e)}"}))
                else:
                    print(f"Error fetching data: {e}", file=sys.stderr)
                sys.exit(3)

        elif args.ortex:
            # Fetch borrow rates from Ortex, prices from CSV
            if not args.json:
                print(f"Fetching {args.days} days of {args.ortex} borrow rates from Ortex...")

            try:
                from .ortex_data import fetch_ortex_borrow_rates
                borrow_data = fetch_ortex_borrow_rates(
                    symbol=args.ortex,
                    days=args.days,
                    api_key=args.ortex_api_key
                )
                if not args.json:
                    print(f"Successfully fetched {len(borrow_data['borrow_rates'])} days of borrow rates")
                    print(f"Loading prices from {args.price_csv}...")
            except Exception as e:
                if args.json:
                    print(json.dumps({"error": f"Ortex fetch failed: {str(e)}"}))
                else:
                    print(f"Error fetching from Ortex: {e}", file=sys.stderr)
                sys.exit(3)

            # Load prices from CSV
            price_csv_data = load_csv_data(
                args.price_csv,
                borrow_rate_col=args.borrow_col,
                price_col=args.price_col,
                require_borrow_rate=False,  # Only need prices
                require_price=True
            )

            # Combine and align
            borrow_rates = borrow_data["borrow_rates"]
            prices = price_csv_data["prices"]
            min_len = min(len(borrow_rates), len(prices))
            if len(borrow_rates) != len(prices) and not args.json:
                print(f"Warning: Data length mismatch. Using most recent {min_len} data points.")
            borrow_rates = borrow_rates[-min_len:]
            prices = prices[-min_len:]

            data = {
                "borrow_rates": borrow_rates,
                "prices": prices
            }

        else:
            # Fetch prices from IBKR, borrow rates from CSV
            try:
                from .ibkr_data import fetch_ibkr_data
            except ImportError:
                print("ERROR: ib_insync library is not installed.")
                print("Install with: pip install ib_insync")
                sys.exit(3)

            if not args.json:
                print(f"Fetching {args.days} days of {args.ibkr} price data from IBKR...")
                print(f"Connecting to {args.host}:{args.port}...")

            try:
                price_data = fetch_ibkr_data(
                    symbol=args.ibkr,
                    days=args.days,
                    host=args.host,
                    port=args.port,
                    client_id=args.client_id
                )
            except Exception as e:
                if args.json:
                    print(json.dumps({"error": f"IBKR connection failed: {str(e)}"}))
                else:
                    print(f"Error connecting to IBKR: {e}", file=sys.stderr)
                sys.exit(3)

            if not args.json:
                print(f"Successfully fetched {len(price_data['prices'])} days of price data")
                print(f"Loading borrow rates from {args.borrow_csv}...")

            # Load borrow rates from CSV
            borrow_data = load_csv_data(
                args.borrow_csv,
                borrow_rate_col=args.borrow_col,
                price_col=args.price_col  # Not used, but required by function
            )

            # Combine data - align lengths if needed
            borrow_rates = borrow_data["borrow_rates"]
            prices = price_data["prices"]

            # Use the shorter length to ensure alignment
            min_len = min(len(borrow_rates), len(prices))
            if len(borrow_rates) != len(prices):
                if not args.json:
                    print(f"Warning: Data length mismatch. Using most recent {min_len} data points.")
                borrow_rates = borrow_rates[-min_len:]
                prices = prices[-min_len:]

            data = {
                "borrow_rates": borrow_rates,
                "prices": prices
            }

        # Run flow state analysis
        monitor = FlowStateMonitor(config)
        results = monitor.analyze(
            borrow_rates=data["borrow_rates"],
            prices=data["prices"]
        )

        # Output results
        if args.json:
            # Make results JSON serializable
            json_results = {
                "market_state": results.get("market_state", "UNKNOWN"),
                "flow_state": results["flow_state"],
                "signal": results.get("signal", "HOLD"),
                "signal_reason": results.get("signal_reason", ""),
                "summary": results["summary"],
                "signals": results["signals"]
            }
            print(json.dumps(json_results, indent=2))
        else:
            # Print the COPILOT_SPEC.md formatted summary
            print(f"\n{results['summary']}\n")

        # Exit with appropriate code based on signal
        # 0 = HOLD/OFF, 1 = BUY, 2 = SELL
        if results.get("signal") == "BUY":
            sys.exit(1)
        elif results.get("signal") == "SELL":
            sys.exit(2)
        else:  # HOLD
            sys.exit(0)

    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
