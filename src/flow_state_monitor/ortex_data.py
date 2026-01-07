"""
Optional Ortex data ingestion module for flow-state-monitor.

This module provides functionality to fetch borrow rate data from Ortex API.
This is an OPTIONAL component - the flow-state-monitor core functionality
works with any data source.

Ortex provides short interest, borrow rates, and other short selling analytics.
Free tier available with limited API calls.

Note: Requires API key from Ortex. Sign up at: https://public.ortex.com/

Example usage:
    >>> from flow_state_monitor.ortex_data import fetch_ortex_borrow_rates
    >>> data = fetch_ortex_borrow_rates('AAPL', days=30, api_key='your-api-key-here')
    >>> # data contains borrow_rates list
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OrtexDataFetcher:
    """
    Fetch borrow rate data from Ortex API.

    This class provides an interface to retrieve historical borrow rate data
    that can be directly used with FlowStateMonitor.

    Requirements:
        - Ortex API key from https://public.ortex.com/
        - Internet connection

    Example:
        >>> fetcher = OrtexDataFetcher(api_key='your-api-key-here')
        >>> data = fetcher.fetch_borrow_rates('AAPL', days=30)
        >>> # Returns dict with 'borrow_rates' key
        >>>
        >>> # Use with monitor
        >>> monitor = FlowStateMonitor()
        >>> results = monitor.analyze(borrow_rates=data['borrow_rates'], prices=prices)
    """

    BASE_URL = "https://api.ortex.com/api/v1"

    def __init__(self, api_key: str):
        """
        Initialize Ortex data fetcher.

        Args:
            api_key: Ortex API key from https://public.ortex.com/
        """
        self.api_key = api_key

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to Ortex API.

        Args:
            endpoint: API endpoint path (e.g., '/stocks/AAPL/short-interest')
            params: Optional query parameters

        Returns:
            JSON response as dictionary

        Raises:
            ConnectionError: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        # Add query parameters
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"

        # Create request with API key header
        headers = {
            'Ortex-Api-Key': self.api_key,
            'Accept': '*/*'
        }

        request = Request(url, headers=headers)

        try:
            with urlopen(request, timeout=30) as response:
                data = response.read()
                return json.loads(data.decode('utf-8'))
        except HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode('utf-8')
            except:
                pass

            if e.code == 401:
                raise ConnectionError(
                    f"Ortex API authentication failed. "
                    f"Check your API key or use 'TEST' for demo access. Details: {error_body}"
                )
            elif e.code == 403:
                raise ConnectionError(
                    f"Ortex API access forbidden. "
                    f"Your API key may not have the required permissions. Details: {error_body}"
                )
            elif e.code == 429:
                raise ConnectionError(
                    "Ortex API rate limit exceeded. "
                    "Wait a moment and try again, or upgrade your API plan."
                )
            else:
                raise ConnectionError(f"Ortex API request failed: {e.code} {e.reason}. Details: {error_body}")
        except URLError as e:
            raise ConnectionError(f"Failed to connect to Ortex API: {str(e.reason)}")
        except Exception as e:
            raise ConnectionError(f"Unexpected error accessing Ortex API: {str(e)}")

    def fetch_borrow_rates(
        self,
        symbol: str,
        days: int = 30,
        end_date: Optional[datetime] = None
    ) -> Dict[str, List[float]]:
        """
        Fetch historical borrow rate data for a symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            days: Number of days of data to fetch (default: 30)
            end_date: End date for historical data (default: today)

        Returns:
            Dictionary with key 'borrow_rates' containing a list of floats
            ordered chronologically (oldest first)

        Raises:
            ConnectionError: If API request fails
            ValueError: If symbol not found or data unavailable

        Note:
            When using 'TEST' as api_key, returns simulated data for testing.
        """
        # Demo mode - return mock data when TEST key is used
        if self.api_key == 'TEST':
            import random
            random.seed(hash(symbol))  # Deterministic per symbol
            base_rate = random.uniform(1.5, 8.0)
            rates = [
                round(base_rate + random.gauss(0, base_rate * 0.2), 2)
                for _ in range(days)
            ]
            return {'borrow_rates': rates}

        if end_date is None:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=days)

        # Format dates for API (YYYY-MM-DD)
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        # Ortex API endpoint for Cost To Borrow data
        # Format: /stock/{exchange_symbol}/{ticker}/ctb/all
        endpoint = f"/stock/US/{symbol.upper()}/ctb/all"
        params = {
            'format': 'json'
        }

        try:
            response = self._make_request(endpoint, params)
        except ConnectionError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {symbol}: {str(e)}")

        # Parse response
        # Ortex CTB response format: { "rows": [{"date": "YYYY-MM-DD", "costToBorrowAll": X.XX}, ...] }
        if 'rows' not in response or not response['rows']:
            raise ValueError(
                f"No borrow rate data available for {symbol}. "
                f"Symbol may not be tracked by Ortex or data unavailable for date range."
            )

        # Extract borrow rates from response
        data_points = response['rows']

        borrow_rates = []
        for point in data_points:
            # costToBorrowAll is returned as annual percentage rate
            if 'costToBorrowAll' in point:
                borrow_rates.append(float(point['costToBorrowAll']))
            else:
                # Skip data points without CTB value
                continue

        if not borrow_rates:
            raise ValueError(
                f"No borrow rate data found in Ortex response for {symbol}. "
                f"The symbol may not have borrow rate information available."
            )

        # Filter to requested date range if needed
        # (API might return more data than requested)
        if len(borrow_rates) > days:
            borrow_rates = borrow_rates[-days:]

        return {
            'borrow_rates': borrow_rates
        }

    def fetch_short_interest(
        self,
        symbol: str,
        days: int = 30
    ) -> Dict[str, any]:
        """
        Fetch comprehensive short interest data including borrow rates.

        Args:
            symbol: Stock ticker symbol
            days: Number of days of data to fetch

        Returns:
            Dictionary with short interest metrics including borrow_rates

        Note: This is a more comprehensive endpoint that returns multiple metrics.
              When using 'TEST' as api_key, returns simulated data for testing.
        """
        # Demo mode
        if self.api_key == 'TEST':
            import random
            random.seed(hash(symbol))
            base_rate = random.uniform(1.5, 8.0)
            base_si = random.uniform(5.0, 25.0)

            return {
                'borrow_rates': [round(base_rate + random.gauss(0, base_rate * 0.2), 2) for _ in range(days)],
                'short_interest_pct': [round(base_si + random.gauss(0, 2.0), 2) for _ in range(days)],
                'days_to_cover': [round(random.uniform(1.0, 5.0), 2) for _ in range(days)],
                'utilization': [round(random.uniform(60.0, 95.0), 2) for _ in range(days)],
            }

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        endpoint = f"/stocks/{symbol.upper()}/short-interest"
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }

        response = self._make_request(endpoint, params)

        if 'data' not in response:
            raise ValueError(f"No data available for {symbol}")

        return response['data']


def fetch_ortex_borrow_rates(
    symbol: str,
    days: int = 30,
    api_key: str = 'TEST',
    **kwargs
) -> Dict[str, List[float]]:
    """
    Convenience function to fetch borrow rates from Ortex.

    Args:
        symbol: Stock ticker symbol
        days: Number of days of data to fetch
        api_key: Ortex API key (default: 'TEST' for demo)
        **kwargs: Additional arguments passed to fetch_borrow_rates()

    Returns:
        Dictionary with 'borrow_rates' key containing list of rates

    Example:
        >>> from flow_state_monitor import FlowStateMonitor
        >>> from flow_state_monitor.ortex_data import fetch_ortex_borrow_rates
        >>> from flow_state_monitor.ibkr_data import fetch_ibkr_data
        >>>
        >>> # Fetch borrow rates from Ortex
        >>> borrow_data = fetch_ortex_borrow_rates('AAPL', days=30, api_key='TEST')
        >>>
        >>> # Fetch price data from IBKR
        >>> price_data = fetch_ibkr_data('AAPL', days=30, port=7497)
        >>>
        >>> # Analyze with monitor
        >>> monitor = FlowStateMonitor()
        >>> results = monitor.analyze(
        ...     borrow_rates=borrow_data['borrow_rates'],
        ...     prices=price_data['prices']
        ... )
    """
    fetcher = OrtexDataFetcher(api_key=api_key)
    return fetcher.fetch_borrow_rates(symbol, days=days, **kwargs)


def fetch_combined_data(
    symbol: str,
    days: int = 30,
    ortex_api_key: str = 'TEST',
    ibkr_port: int = 7497,
    ibkr_host: str = '127.0.0.1',
    ibkr_client_id: int = 1
) -> Dict[str, List[float]]:
    """
    Fetch both borrow rates (Ortex) and prices (IBKR) in one call.

    This convenience function fetches data from both sources and returns
    a combined dictionary ready for FlowStateMonitor.

    Args:
        symbol: Stock ticker symbol
        days: Number of days of data to fetch
        ortex_api_key: Ortex API key
        ibkr_port: IBKR TWS/Gateway port
        ibkr_host: IBKR TWS/Gateway host
        ibkr_client_id: IBKR client ID

    Returns:
        Dictionary with 'borrow_rates' and 'prices' keys

    Example:
        >>> from flow_state_monitor import FlowStateMonitor
        >>> from flow_state_monitor.ortex_data import fetch_combined_data
        >>>
        >>> # Fetch both borrow rates and prices
        >>> data = fetch_combined_data('AAPL', days=30, ortex_api_key='YOUR_KEY')
        >>>
        >>> # Analyze
        >>> monitor = FlowStateMonitor()
        >>> results = monitor.analyze(**data)
    """
    # Fetch borrow rates from Ortex
    borrow_data = fetch_ortex_borrow_rates(symbol, days=days, api_key=ortex_api_key)

    # Fetch prices from IBKR
    try:
        from .ibkr_data import fetch_ibkr_data
        price_data = fetch_ibkr_data(
            symbol,
            days=days,
            host=ibkr_host,
            port=ibkr_port,
            client_id=ibkr_client_id
        )
    except ImportError:
        raise ImportError(
            "IBKR integration not available. "
            "Install ib_insync: pip install ib_insync"
        )

    # Align data lengths
    borrow_rates = borrow_data['borrow_rates']
    prices = price_data['prices']

    min_len = min(len(borrow_rates), len(prices))
    if len(borrow_rates) != len(prices):
        # Use most recent data points
        borrow_rates = borrow_rates[-min_len:]
        prices = prices[-min_len:]

    return {
        'borrow_rates': borrow_rates,
        'prices': prices
    }
