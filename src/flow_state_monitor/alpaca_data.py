"""
Optional Alpaca data ingestion module for flow-state-monitor.

This module provides functionality to fetch daily price data from Alpaca Markets
using the alpaca-py library. This is an OPTIONAL component - the
flow-state-monitor core functionality works with any data source.

Note: Requires alpaca-py to be installed separately:
    pip install alpaca-py

Alpaca provides commission-free trading and market data for US equities.
Sign up at https://alpaca.markets/ for API keys.

Important: Alpaca only supports US equities. Forex, futures, and international
stocks are not available.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AlpacaDataFetcher:
    """
    Fetch daily price data from Alpaca Markets.

    This class provides a simple interface to retrieve historical daily bar data
    from Alpaca that can be directly used with FlowStateMonitor.

    Requirements:
        - alpaca-py library installed
        - Alpaca API key and secret key (get free account at alpaca.markets)

    Example:
        >>> fetcher = AlpacaDataFetcher(api_key='YOUR_KEY', secret_key='YOUR_SECRET')
        >>> data = fetcher.fetch_daily_bars('AAPL', days=30)
        >>>
        >>> # Use with monitor
        >>> from flow_state_monitor import FlowStateMonitor
        >>> monitor = FlowStateMonitor()
        >>> # Combine with borrow rate data from Ortex
        >>> results = monitor.analyze(borrow_rates=borrow_data, prices=data['prices'])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: bool = True
    ):
        """
        Initialize Alpaca data fetcher.

        Args:
            api_key: Alpaca API key (or set ALPACA_API_KEY environment variable)
            secret_key: Alpaca secret key (or set ALPACA_SECRET_KEY environment variable)
            paper: Kept only for API consistency (default: True). This parameter
                   does not affect data fetching; historical data access uses the
                   same endpoint for both paper and live keys. The paper/live
                   distinction matters only for trading operations.

        Note:
            Paper trading is recommended for testing and development.
            API keys from paper and live accounts are different.
        """
        # Get API keys from parameters or environment variables
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')

        if not self.api_key or not self.secret_key:
            raise ValueError(
                "API key and secret key are required. "
                "Provide them as parameters or set ALPACA_API_KEY and "
                "ALPACA_SECRET_KEY environment variables."
            )

        self.paper = paper
        self.client = None

    def _validate_symbol(self, symbol: str) -> None:
        """
        Validate that symbol is a US equity (not forex/futures).

        Args:
            symbol: Ticker symbol to validate

        Raises:
            ValueError: If symbol appears to be forex, futures, or other non-equity
        """
        symbol_upper = symbol.upper()

        # Check for forex patterns
        if '/' in symbol_upper:
            raise ValueError(
                f"Symbol '{symbol}' appears to be a forex pair. "
                f"Alpaca only supports US equities. "
                f"Try stock symbols like 'AAPL', 'MSFT', 'TSLA'."
            )

        # Check for common forex currency codes (6 chars like EURUSD)
        # Only flag if BOTH parts are valid currency codes to avoid false positives
        if len(symbol_upper) == 6 and symbol_upper.isalpha():
            common_currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD', 'USD']
            first_three = symbol_upper[:3]
            last_three = symbol_upper[3:]
            # Both parts must be currencies AND different to be a forex pair
            if (first_three in common_currencies and
                last_three in common_currencies and
                first_three != last_three):
                raise ValueError(
                    f"Symbol '{symbol}' appears to be a forex pair ({first_three}/{last_three}). "
                    f"Alpaca only supports US equities."
                )

        # Check for futures indicators
        common_futures_roots = ['ES', 'CL', 'GC', 'NQ', 'YM', 'RTY', 'ZN', 'ZB', 'ZC', 'ZS', 'NG']

        if symbol_upper in common_futures_roots:
            raise ValueError(
                f"Symbol '{symbol}' appears to be a futures contract. "
                f"Alpaca only supports US equities."
            )

        if len(symbol_upper) >= 4:
            for root in common_futures_roots:
                if symbol_upper.startswith(root) and len(symbol_upper) == len(root) + 3:
                    remainder = symbol_upper[len(root):]
                    if len(remainder) == 3 and remainder[0].isalpha() and remainder[1:].isdigit():
                        raise ValueError(
                            f"Symbol '{symbol}' appears to be a futures contract. "
                            f"Alpaca only supports US equities."
                        )

        if 'FUT' in symbol_upper:
            raise ValueError(
                f"Symbol '{symbol}' appears to be a futures contract. "
                f"Alpaca only supports US equities."
            )

    def _get_client(self):
        """
        Lazy initialization of Alpaca client.

        Returns:
            StockHistoricalDataClient instance
        """
        if self.client is None:
            try:
                from alpaca.data.historical import StockHistoricalDataClient
            except ImportError:
                raise ImportError(
                    "alpaca-py library is required for Alpaca data fetching. "
                    "Install with: pip install alpaca-py"
                )

            self.client = StockHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.secret_key
            )

        return self.client

    def fetch_daily_bars(
        self,
        symbol: str,
        days: int = 30,
        end_date: Optional[datetime] = None
    ) -> Dict[str, List[float]]:
        """
        Fetch daily price bars for a symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
                Note: Only US equities are supported
            days: Number of daily bars to fetch (default: 30)
            end_date: End date for historical data (default: today)

        Returns:
            Dictionary with key 'prices' containing a list of closing prices
            ordered chronologically (oldest first)

        Raises:
            ValueError: If symbol is not a US equity or data unavailable
            ImportError: If alpaca-py is not installed
        """
        self._validate_symbol(symbol)
        client = self._get_client()

        try:
            from alpaca.data.enums import DataFeed
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame
        except ImportError:
            raise ImportError("alpaca-py library is required")

        if end_date is None:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=days + 10)

        request = StockBarsRequest(
            symbol_or_symbols=symbol.upper(),
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date,
            feed=DataFeed.IEX
        )

        try:
            bars_response = client.get_stock_bars(request)
        except Exception as e:
            raise ValueError(
                f"Failed to fetch data for '{symbol}'. "
                f"Error: {str(e)}"
            )

        symbol_key = symbol.upper()

        bars = None
        if hasattr(bars_response, 'data') and symbol_key in bars_response.data:
            bars = bars_response.data[symbol_key]
        elif symbol_key in bars_response:
            bars = bars_response[symbol_key]
        elif hasattr(bars_response, symbol_key):
            bars = getattr(bars_response, symbol_key)

        if bars is None:
            raise ValueError(
                f"Unexpected response format when fetching data for '{symbol}'. "
                f"Unable to locate bar data for symbol key '{symbol_key}'."
            )
        elif not bars:
            raise ValueError(
                f"No data returned for '{symbol}'. "
                f"Check that the symbol is valid and has trading data."
            )

        bars_list = sorted(bars, key=lambda x: x.timestamp)
        bars_list = bars_list[-days:] if len(bars_list) > days else bars_list

        if len(bars_list) < days:
            logger.info(
                f"Only {len(bars_list)} bars available for '{symbol}' "
                f"(requested {days})."
            )

        prices = [float(bar.close) for bar in bars_list]

        return {'prices': prices}

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass


def fetch_alpaca_prices(
    symbol: str,
    days: int = 30,
    api_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    paper: bool = True,
    **kwargs
) -> Dict[str, List[float]]:
    """
    Convenience function to fetch Alpaca price data.

    Args:
        symbol: Stock ticker symbol (US equities only)
        days: Number of daily bars to fetch
        api_key: Alpaca API key (or set ALPACA_API_KEY env var)
        secret_key: Alpaca secret key (or set ALPACA_SECRET_KEY env var)
        paper: Use paper trading endpoint (default: True)
        **kwargs: Additional arguments passed to fetch_daily_bars()

    Returns:
        Dictionary with 'prices' key containing closing prices
    """
    with AlpacaDataFetcher(api_key=api_key, secret_key=secret_key, paper=paper) as fetcher:
        return fetcher.fetch_daily_bars(symbol, days=days, **kwargs)


def fetch_combined_data(
    symbol: str,
    days: int = 30,
    ortex_api_key: str = None,
    alpaca_api_key: Optional[str] = None,
    alpaca_secret_key: Optional[str] = None,
    paper: bool = True
) -> Dict[str, List[float]]:
    """
    Fetch both borrow rates from Ortex and prices from Alpaca.

    Args:
        symbol: Stock ticker symbol (US equities only)
        days: Number of days of data to fetch
        ortex_api_key: Ortex API key (or set ORTEX_API_KEY env var)
        alpaca_api_key: Alpaca API key (or set ALPACA_API_KEY env var)
        alpaca_secret_key: Alpaca secret key (or set ALPACA_SECRET_KEY env var)
        paper: Use Alpaca paper trading endpoint (default: True)

    Returns:
        Dictionary with 'borrow_rates' and 'prices' keys
    """
    try:
        from .ortex_data import fetch_ortex_borrow_rates
    except ImportError:
        raise ImportError("Ortex data module is required.")

    borrow_data = fetch_ortex_borrow_rates(
        symbol=symbol,
        days=days,
        api_key=ortex_api_key
    )

    price_data = fetch_alpaca_prices(
        symbol=symbol,
        days=days,
        api_key=alpaca_api_key,
        secret_key=alpaca_secret_key,
        paper=paper
    )

    borrow_rates = borrow_data['borrow_rates']
    prices = price_data['prices']

    min_len = min(len(borrow_rates), len(prices))
    if len(borrow_rates) != len(prices):
        logger.warning(
            f"Data length mismatch: {len(borrow_rates)} borrow rates vs {len(prices)} prices. "
            f"Using most recent {min_len} data points."
        )
        borrow_rates = borrow_rates[-min_len:]
        prices = prices[-min_len:]

    return {
        'borrow_rates': borrow_rates,
        'prices': prices
    }
