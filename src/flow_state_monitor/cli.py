"""
Command-line interface for flow state monitor.

This module provides a CLI for analyzing market data from CSV files to
detect flow states driven by forced buying pressure.
"""

import argparse
import csv
import json
import os
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
        description="Monitor market flow states driven by forced buying pressure (uses Ortex + Alpaca by default).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch borrow rates from Ortex and prices from Alpaca (default mode)
  flow-state-monitor AAPL

  # Same as above with explicit days parameter
  flow-state-monitor AAPL --days 30

  # Analyze data from CSV file
  flow-state-monitor --csv data.csv

  # Fetch borrow rates from Ortex with prices from CSV
  flow-state-monitor AAPL --price-csv prices.csv

  # Override API keys from environment
  flow-state-monitor AAPL --ortex-api-key YOUR_KEY --alpaca-api-key YOUR_KEY

  # Use IBKR instead of Alpaca for prices
  flow-state-monitor AAPL --use-ibkr

  # Use Ortex demo key for testing
  flow-state-monitor AAPL --ortex-api-key TEST --price-csv prices.csv

  # Use custom config file
  flow-state-monitor AAPL --config custom_config.yaml

  # Get JSON output for scripting
  flow-state-monitor --csv data.csv --json

Note: This tool monitors flow states to support disciplined exits.
      It is NOT a trading signal or prediction tool.

Data Sources:
  - Ortex: Provides borrow rate data (default, requires ORTEX_API_KEY env var)
  - Alpaca: Provides price data (default, requires ALPACA_API_KEY and ALPACA_SECRET_KEY env vars)
  - IBKR: Alternative price source (use --use-ibkr flag)
  - CSV: Provides any data from file

Environment Variables:
  - ORTEX_API_KEY: Ortex API key (use 'TEST' for demo)
  - ALPACA_API_KEY: Alpaca API key (get from alpaca.markets)
  - ALPACA_SECRET_KEY: Alpaca secret key
  - IBKR_PORT: IBKR TWS/Gateway port (default: 7497)
  - IBKR_HOST: IBKR TWS/Gateway host (default: 127.0.0.1)
        """
    )

    parser.add_argument(
        "symbol",
        type=str,
        nargs="?",
        metavar="SYMBOL",
        help="Stock symbol to monitor (uses IBKR Borrow Sensor for borrow rates, Alpaca for prices by default)"
    )

    parser.add_argument(
        "--csv",
        type=str,
        help="Path to CSV file containing market data (standalone mode, no symbol needed)"
    )

    parser.add_argument(
        "--ibkr-snapshot-dir",
        type=str,
        default="./output",
        help="Directory containing IBKR borrow snapshot JSON files (default: ./output)"
    )

    parser.add_argument(
        "--alpaca-api-key",
        type=str,
        default=None,
        help="Alpaca API key (default: from ALPACA_API_KEY env var)"
    )

    parser.add_argument(
        "--alpaca-secret-key",
        type=str,
        default=None,
        help="Alpaca secret key (default: from ALPACA_SECRET_KEY env var)"
    )

    parser.add_argument(
        "--price-csv",
        type=str,
        help="CSV file with price data (use instead of API sources)"
    )

    parser.add_argument(
        "--use-ibkr",
        action="store_true",
        help="Use IBKR for price data instead of Alpaca (requires TWS/Gateway running)"
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
        default=None,
        help="IBKR TWS/Gateway port (default: from IBKR_PORT env var or 7497)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="IBKR TWS/Gateway host address (default: from IBKR_HOST env var or 127.0.0.1)"
    )

    parser.add_argument(
        "--client-id",
        type=int,
        default=1,
        help="IBKR client ID (default: 1)"
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

    # Get environment variables with defaults
    ibkr_snapshot_dir = args.ibkr_snapshot_dir or os.getenv('IBKR_SNAPSHOT_DIR', './output')
    alpaca_api_key = args.alpaca_api_key or os.getenv('ALPACA_API_KEY')
    alpaca_secret_key = args.alpaca_secret_key or os.getenv('ALPACA_SECRET_KEY')
    ibkr_port = args.port if args.port is not None else int(os.getenv('IBKR_PORT', '7497'))
    ibkr_host = args.host or os.getenv('IBKR_HOST', '127.0.0.1')

    # Validate arguments
    has_csv = args.csv is not None
    has_symbol = args.symbol is not None

    # At least one data source required
    if not has_csv and not has_symbol:
        parser.error("Either SYMBOL or --csv required")

    # CSV is standalone
    if has_csv and has_symbol:
        parser.error("Cannot use SYMBOL with --csv (CSV provides all data)")

    # Validate symbol mode requirements
    if has_symbol and not args.price_csv and not args.use_ibkr:
        # Default mode: need Alpaca credentials
        if not alpaca_api_key or not alpaca_secret_key:
            parser.error(
                "Alpaca credentials not found (default price source).\n"
                "\n"
                "Option 1: Set environment variables (before running command):\n"
                "  export ALPACA_API_KEY=your_key\n"
                "  export ALPACA_SECRET_KEY=your_secret\n"
                "  Get free keys from https://alpaca.markets/\n"
                "\n"
                "Option 2: Pass credentials via command-line arguments:\n"
                "  flow-state-monitor AAPL --alpaca-api-key KEY --alpaca-secret-key SECRET\n"
                "\n"
                "Option 3: Use CSV for prices:\n"
                "  flow-state-monitor AAPL --price-csv FILE\n"
                "\n"
                "Option 4: Use IBKR instead:\n"
                "  flow-state-monitor AAPL --use-ibkr\n"
                "  (Requires: pip install ib_insync)"
            )
        # Check if alpaca-py is installed
        try:
            import alpaca.data.historical
        except ImportError:
            parser.error(
                "alpaca-py library is required for Alpaca price data.\n"
                "Install with: pip install alpaca-py\n"
                "Or use alternative: --price-csv FILE or --use-ibkr"
            )
    elif has_symbol and args.price_csv and args.use_ibkr:
        parser.error("Cannot use both --price-csv and --use-ibkr")

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
        elif has_symbol:
            # Symbol mode: IBKR Borrow Sensor for borrow rates, Alpaca/IBKR/CSV for prices
            if args.price_csv:
                # Fetch borrow rates from IBKR Borrow Sensor, prices from CSV
                if not args.json:
                    print(f"Fetching {args.days} days of {args.symbol} borrow rates from IBKR Borrow Sensor...")

                try:
                    from .ibkr_borrow_data import fetch_ibkr_borrow_rates
                    borrow_data = fetch_ibkr_borrow_rates(
                        symbol=args.symbol,
                        days=args.days,
                        snapshot_dir=ibkr_snapshot_dir
                    )

                    # Load prices from CSV
                    price_data = load_csv_data(
                        args.price_csv,
                        borrow_rate_col=None,
                        price_col=args.price_col,
                        require_borrow_rate=False,
                        require_price=True
                    )

                    data = {
                        "borrow_rates": borrow_data["borrow_rates"],
                        "prices": price_data["prices"]
                    }

                    if not args.json:
                        print(f"Successfully fetched {len(data['borrow_rates'])} days of data")
                except Exception as e:
                    if args.json:
                        print(json.dumps({"error": f"Data fetch failed: {str(e)}"}))
                    else:
                        print(f"Error fetching data: {e}", file=sys.stderr)
                    sys.exit(3)
            elif args.use_ibkr:
                # Fetch borrow rates from IBKR Borrow Sensor and prices from IBKR
                if not args.json:
                    print(f"Fetching data for {args.symbol} from IBKR Borrow Sensor and IBKR...")

                try:
                    from .ibkr_data import fetch_combined_data
                    data = fetch_combined_data(
                        symbol=args.symbol,
                        days=args.days,
                        ibkr_snapshot_dir=ibkr_snapshot_dir,
                        ibkr_port=ibkr_port,
                        ibkr_host=ibkr_host,
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
            else:
                # Default mode: Fetch borrow rates from IBKR Borrow Sensor and prices from Alpaca
                if not args.json:
                    print(f"Fetching data for {args.symbol} from IBKR Borrow Sensor and Alpaca...")

                try:
                    from .alpaca_data import fetch_combined_data
                    data = fetch_combined_data(
                        symbol=args.symbol,
                        days=args.days,
                        ibkr_snapshot_dir=ibkr_snapshot_dir,
                        alpaca_api_key=alpaca_api_key,
                        alpaca_secret_key=alpaca_secret_key,
                        paper=True
                    )
                    if not args.json:
                        print(f"Successfully fetched {len(data['borrow_rates'])} days of data")
                except Exception as e:
                    if args.json:
                        print(json.dumps({"error": f"Data fetch failed: {str(e)}"}))
                    else:
                        print(f"Error fetching data: {e}", file=sys.stderr)
                    sys.exit(3)

        # Fetch benchmark data for relative strength analysis (if using live data)
        relative_strength = None
        fetcher = None
        if has_symbol and not args.price_csv:
            try:
                if not args.json:
                    print("Fetching benchmark data (SPY, QQQ)...")

                from .market_context import MarketContextAnalyzer
                analyzer = MarketContextAnalyzer()

                # Use the same data fetcher as for stock data
                if args.use_ibkr:
                    from .ibkr_data import IBKRDataFetcher
                    with IBKRDataFetcher(port=ibkr_port, host=ibkr_host, client_id=args.client_id) as fetcher:
                        benchmark_prices = analyzer.get_benchmark_prices(fetcher, days=args.days)
                else:
                    # Default: Alpaca - create single fetcher for both stock and benchmark data
                    # Note: Stock data was already fetched via fetch_combined_data above
                    # This fetcher is only used for benchmark data
                    from .alpaca_data import AlpacaDataFetcher
                    with AlpacaDataFetcher(api_key=alpaca_api_key, secret_key=alpaca_secret_key, paper=True) as fetcher:
                        benchmark_prices = analyzer.get_benchmark_prices(fetcher, days=args.days)

                # Calculate relative strength
                relative_strength = analyzer.analyze_relative_strength(
                    symbol=args.symbol,
                    stock_prices=data["prices"],
                    benchmark_prices=benchmark_prices
                )

                if not args.json:
                    print("Benchmark data fetched successfully")
            except Exception as e:
                # Non-critical - continue without relative strength
                if not args.json:
                    print(f"Warning: Could not fetch benchmark data: {e}")

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

            # Add relative strength data if available
            if relative_strength:
                json_results["relative_strength"] = {
                    "stock_return": relative_strength.stock_return,
                    "spy_return": relative_strength.spy_return,
                    "qqq_return": relative_strength.qqq_return,
                    "spy_relative": relative_strength.spy_relative,
                    "qqq_relative": relative_strength.qqq_relative,
                    "outperforming_spy": relative_strength.outperforming_spy,
                    "outperforming_qqq": relative_strength.outperforming_qqq,
                    "description": relative_strength.description
                }

            print(json.dumps(json_results, indent=2))
        else:
            # Print the COPILOT_SPEC.md formatted summary
            print(f"\n{results['summary']}\n")

            # Add relative strength analysis if available
            if relative_strength:
                from .market_context import (
                    check_narrative_boundary,
                    format_relative_strength,
                )
                print(format_relative_strength(relative_strength, results["flow_state"]))

                # Check if we're at the boundary between money flow and narrative domains
                borrow_rate = data["borrow_rates"][-1] if data["borrow_rates"] else 0.0
                boundary_hint = check_narrative_boundary(
                    relative_strength,
                    results["flow_state"],
                    borrow_rate
                )
                if boundary_hint:
                    print(boundary_hint)

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
