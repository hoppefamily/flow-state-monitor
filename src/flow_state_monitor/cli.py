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
from typing import List, Dict

from . import __version__
from .monitor import FlowStateMonitor
from .config import Config


def load_csv_data(
    filepath: str,
    borrow_rate_col: str = "borrow_rate",
    price_col: str = "close"
) -> Dict[str, List[float]]:
    """
    Load market data from CSV file.
    
    Args:
        filepath: Path to CSV file
        borrow_rate_col: Column name for borrow rates
        price_col: Column name for closing prices
        
    Returns:
        Dictionary with borrow_rates and prices lists
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    data = {
        "borrow_rates": [],
        "prices": []
    }
    
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if borrow_rate_col not in row:
                raise ValueError(f"Required column '{borrow_rate_col}' not found in CSV")
            if price_col not in row:
                raise ValueError(f"Required column '{price_col}' not found in CSV")
            
            data["borrow_rates"].append(float(row[borrow_rate_col]))
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
  
  # Use custom config file
  flow-state-monitor --csv data.csv --config custom_config.yaml
  
  # Specify custom column names
  flow-state-monitor --csv data.csv --borrow-col borrow --price-col price
  
  # Get JSON output for scripting
  flow-state-monitor --csv data.csv --json

Note: This tool monitors flow states to support disciplined exits.
      It is NOT a trading signal or prediction tool.
        """
    )
    
    parser.add_argument(
        "--csv",
        type=str,
        help="Path to CSV file containing market data"
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
    if not args.csv:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Load configuration
        config = Config(args.config) if args.config else Config()
        
        # Load data
        data = load_csv_data(
            args.csv,
            borrow_rate_col=args.borrow_col,
            price_col=args.price_col
        )
        
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
                "flow_state": results["flow_state"],
                "summary": results["summary"],
                "signals": results["signals"]
            }
            print(json.dumps(json_results, indent=2))
        else:
            print("\n" + "="*60)
            print("FLOW STATE MONITOR - ANALYSIS RESULTS")
            print("="*60)
            print(f"\n{results['summary']}\n")
            
            # Display detailed signals
            print("SIGNAL DETAILS:")
            print("-" * 60)
            
            # Borrow level
            if "borrow_level" in results["signals"]:
                level_sig = results["signals"]["borrow_level"]
                print(f"\n• BORROW RATE LEVEL: {level_sig['level']}")
                if "details" in level_sig:
                    details = level_sig["details"]
                    print(f"  Current rate: {details['borrow_rate']:.2f}%")
            
            # Borrow delta
            if "borrow_delta" in results["signals"]:
                delta_sig = results["signals"]["borrow_delta"]
                print(f"\n• BORROW RATE CHANGE: {delta_sig['change_type']}")
                if "details" in delta_sig:
                    details = delta_sig["details"]
                    print(f"  Delta: {details['delta']:+.2f} pct points")
                    print(f"  Previous: {details['previous_rate']:.2f}% → Current: {details['current_rate']:.2f}%")
            
            # Borrow momentum
            if "borrow_momentum" in results["signals"]:
                momentum_sig = results["signals"]["borrow_momentum"]
                print(f"\n• BORROW RATE MOMENTUM: {momentum_sig['momentum_type']}")
                if "details" in momentum_sig:
                    details = momentum_sig["details"]
                    print(f"  Momentum: {details['momentum']:+.2f} pct points/day")
                    print(f"  Period: {details['period_days']} days")
            
            # Price spike
            if "price_spike" in results["signals"]:
                spike_sig = results["signals"]["price_spike"]
                detected = "YES" if spike_sig["detected"] else "NO"
                print(f"\n• PRICE SPIKE DETECTED: {detected}")
                if "details" in spike_sig:
                    details = spike_sig["details"]
                    print(f"  Recent return: {details['recent_return']:+.2f}%")
            
            # Abnormal volatility
            if "abnormal_volatility" in results["signals"]:
                vol_sig = results["signals"]["abnormal_volatility"]
                detected = "YES" if vol_sig["detected"] else "NO"
                print(f"\n• ABNORMAL VOLATILITY: {detected}")
                if "details" in vol_sig:
                    details = vol_sig["details"]
                    print(f"  Recent return: {details['recent_return']:.2f}%")
                    print(f"  Historical volatility: {details['historical_volatility']:.2f}%")
            
            print("\n" + "="*60 + "\n")
        
        # Exit with appropriate code
        # 0 = OFF, 1 = ON, 2 = WEAKENING
        if results["flow_state"] == "OFF":
            sys.exit(0)
        elif results["flow_state"] == "ON":
            sys.exit(1)
        else:  # WEAKENING
            sys.exit(2)
        
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
