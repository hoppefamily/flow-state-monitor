"""
Tests for IBKR data fetcher.

Note: These tests do NOT require a live IBKR connection. They test the
module structure and error handling. Integration testing with a real
IBKR connection should be done manually.
"""

import pytest

from flow_state_monitor.ibkr_data import IBKRDataFetcher


def test_ibkr_fetcher_initialization():
    """Test that IBKRDataFetcher can be initialized with default parameters."""
    fetcher = IBKRDataFetcher()
    assert fetcher.host == '127.0.0.1'
    assert fetcher.port == 7497
    assert fetcher.client_id == 1
    assert fetcher.ib is None
    assert not fetcher.is_connected()


def test_ibkr_fetcher_custom_initialization():
    """Test that IBKRDataFetcher can be initialized with custom parameters."""
    fetcher = IBKRDataFetcher(host='192.168.1.100', port=4001, client_id=5)
    assert fetcher.host == '192.168.1.100'
    assert fetcher.port == 4001
    assert fetcher.client_id == 5


def test_not_connected_error():
    """Test that fetch_daily_bars raises error when not connected."""
    fetcher = IBKRDataFetcher()
    with pytest.raises(ConnectionError, match="Not connected to IBKR"):
        fetcher.fetch_daily_bars('AAPL')


def test_disconnect_when_not_connected():
    """Test that disconnect works even when not connected."""
    fetcher = IBKRDataFetcher()
    fetcher.disconnect()  # Should not raise error
    assert not fetcher.is_connected()


def test_context_manager_interface():
    """Test that IBKRDataFetcher has context manager methods."""
    fetcher = IBKRDataFetcher()
    assert hasattr(fetcher, '__enter__')
    assert hasattr(fetcher, '__exit__')


def test_fetch_ibkr_data_function_exists():
    """Test that convenience function is importable."""
    from flow_state_monitor.ibkr_data import fetch_ibkr_data
    assert callable(fetch_ibkr_data)


def test_missing_ib_insync_error():
    """Test that proper error is raised when ib_insync is not available."""
    # This test will pass if ib_insync is not installed
    # If ib_insync IS installed, it will test that connect works
    fetcher = IBKRDataFetcher()
    try:
        import ib_insync
        # If ib_insync is installed, we can't test the ImportError
        # but we can verify the connect method exists
        assert hasattr(fetcher, 'connect')
    except ImportError:
        # ib_insync not installed - test the error handling
        with pytest.raises(ImportError, match="ib_insync"):
            fetcher.connect()


# Note: The following tests would require a live IBKR connection
# and should be run manually when TWS/Gateway is available:
#
# def test_real_connection():
#     """Requires TWS/Gateway running on port 7497"""
#     with IBKRDataFetcher(port=7497) as fetcher:
#         data = fetcher.fetch_daily_bars('AAPL', days=5)
#         assert 'prices' in data
#         assert len(data['prices']) > 0
#
# def test_real_multiple_symbols():
#     """Requires TWS/Gateway running on port 7497"""
#     with IBKRDataFetcher(port=7497) as fetcher:
#         data = fetcher.fetch_multiple_symbols(['AAPL', 'MSFT'], days=5)
#         assert 'AAPL' in data
#         assert 'MSFT' in data
