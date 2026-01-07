"""
IBKR Borrow Sensor integration module for flow-state-monitor.

This module provides functionality to fetch borrow rate data from ibkr-borrow-sensor
JSON snapshots. This is an OPTIONAL component - the flow-state-monitor core
functionality works with any data source.

The ibkr-borrow-sensor scrapes IBKR Client Portal for borrow availability and rates,
providing coarse-grained state buckets suitable for flow monitoring.

Example usage:
    >>> from flow_state_monitor.ibkr_borrow_data import fetch_ibkr_borrow_rates
    >>> data = fetch_ibkr_borrow_rates('AAPL', snapshot_dir='./output')
    >>> # data contains borrow_rates list
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class IBKRBorrowDataFetcher:
    """
    Fetch borrow rate data from IBKR Borrow Sensor JSON snapshots.

    This class provides an interface to retrieve borrow rate data from
    ibkr-borrow-sensor snapshot files that can be directly used with FlowStateMonitor.

    Requirements:
        - ibkr-borrow-sensor running and generating snapshots
        - Access to snapshot directory (default: ./output)

    Example:
        >>> fetcher = IBKRBorrowDataFetcher(snapshot_dir='./output')
        >>> data = fetcher.fetch_borrow_rates('AAPL', days=30)
        >>> # Returns dict with 'borrow_rates' key
        >>>
        >>> # Use with monitor
        >>> monitor = FlowStateMonitor()
        >>> results = monitor.analyze(borrow_rates=data['borrow_rates'], prices=prices)
    """

    # Rate bucket to percentage mapping (approximate midpoints)
    RATE_BUCKETS = {
        'VERY_LOW': 0.5,
        'LOW': 2.0,
        'MEDIUM': 5.0,
        'HIGH': 10.0,
        'VERY_HIGH': 25.0,
        'EXTREME': 50.0,
        'UNKNOWN': 0.0
    }

    def __init__(self, snapshot_dir: str = './output'):
        """
        Initialize IBKR Borrow Data Fetcher.

        Args:
            snapshot_dir: Path to ibkr-borrow-sensor output directory
        """
        self.snapshot_dir = Path(snapshot_dir)
        if not self.snapshot_dir.exists():
            raise ValueError(f"Snapshot directory not found: {snapshot_dir}")

    def _read_snapshot(self, symbol: str) -> Optional[Dict]:
        """Read the latest snapshot for a symbol."""
        snapshot_file = self.snapshot_dir / f"borrow-state-{symbol}-latest.json"

        if not snapshot_file.exists():
            logger.warning(f"No snapshot found for {symbol}")
            return None

        try:
            with open(snapshot_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read snapshot for {symbol}: {e}")
            return None

    def _rate_to_percentage(self, rate_bucket: str) -> float:
        """Convert rate bucket to percentage."""
        return self.RATE_BUCKETS.get(rate_bucket, 0.0)

    def fetch_borrow_rates(
        self,
        symbol: str,
        days: int = 30
    ) -> Dict[str, List[float]]:
        """
        Fetch borrow rates from IBKR snapshot.

        Note: Since ibkr-borrow-sensor provides point-in-time state, not historical
        data, this returns a single rate value repeated for the requested days.
        For historical analysis, you would need to collect snapshots over time.

        Args:
            symbol: Stock ticker symbol
            days: Number of days (used to repeat current rate for compatibility)

        Returns:
            Dictionary with 'borrow_rates' key containing list of rates

        Raises:
            ValueError: If symbol data cannot be fetched
        """
        snapshot = self._read_snapshot(symbol)

        if not snapshot:
            raise ValueError(
                f"No borrow data available for {symbol}. "
                f"Ensure ibkr-borrow-sensor is running and has generated snapshots."
            )

        # Extract rate from snapshot
        rate_bucket = snapshot.get('rate', 'UNKNOWN')
        rate_percentage = self._rate_to_percentage(rate_bucket)

        logger.info(
            f"IBKR borrow rate for {symbol}: {rate_bucket} (~{rate_percentage}%)"
        )

        # Since we only have current state, repeat the rate for requested days
        # In production, you would ideally collect historical snapshots
        borrow_rates = [rate_percentage] * days

        return {
            'borrow_rates': borrow_rates,
            'rate_bucket': rate_bucket,
            'availability': snapshot.get('availability', 'UNKNOWN'),
            'change_direction': snapshot.get('changeDirection', 'UNKNOWN'),
            'timestamp': snapshot.get('timestamp')
        }


def fetch_ibkr_borrow_rates(
    symbol: str,
    days: int = 30,
    snapshot_dir: str = './output',
    **kwargs
) -> Dict[str, List[float]]:
    """
    Convenience function to fetch borrow rates from IBKR snapshots.

    Args:
        symbol: Stock ticker symbol
        days: Number of days of data (rate repeated for compatibility)
        snapshot_dir: Path to ibkr-borrow-sensor output directory
        **kwargs: Additional arguments (for compatibility)

    Returns:
        Dictionary with 'borrow_rates' key containing list of rates

    Example:
        >>> from flow_state_monitor import FlowStateMonitor
        >>> from flow_state_monitor.ibkr_borrow_data import fetch_ibkr_borrow_rates
        >>> from flow_state_monitor.alpaca_data import fetch_alpaca_prices
        >>>
        >>> # Fetch borrow rates from IBKR sensor
        >>> borrow_data = fetch_ibkr_borrow_rates('AAPL', days=30)
        >>>
        >>> # Fetch price data from Alpaca
        >>> price_data = fetch_alpaca_prices('AAPL', days=30)
        >>>
        >>> # Analyze with monitor
        >>> monitor = FlowStateMonitor()
        >>> results = monitor.analyze(
        ...     borrow_rates=borrow_data['borrow_rates'],
        ...     prices=price_data['prices']
        ... )
    """
    fetcher = IBKRBorrowDataFetcher(snapshot_dir=snapshot_dir)
    return fetcher.fetch_borrow_rates(symbol, days=days)
