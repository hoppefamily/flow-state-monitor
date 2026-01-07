"""Tests for IBKR Borrow Sensor data fetcher.

These tests are offline-only and validate:
- rate bucket mapping
- expected snapshot filename
- error handling when snapshot dir / file missing
"""

from pathlib import Path

import pytest

from flow_state_monitor.ibkr_borrow_data import (
    IBKRBorrowDataFetcher,
    fetch_ibkr_borrow_rates,
)


def test_rate_bucket_mapping():
    assert IBKRBorrowDataFetcher.RATE_BUCKETS["VERY_LOW"] == 0.5
    assert IBKRBorrowDataFetcher.RATE_BUCKETS["LOW"] == 2.0
    assert IBKRBorrowDataFetcher.RATE_BUCKETS["MEDIUM"] == 5.0
    assert IBKRBorrowDataFetcher.RATE_BUCKETS["HIGH"] == 10.0
    assert IBKRBorrowDataFetcher.RATE_BUCKETS["VERY_HIGH"] == 25.0
    assert IBKRBorrowDataFetcher.RATE_BUCKETS["EXTREME"] == 50.0


def test_init_raises_for_missing_snapshot_dir(tmp_path: Path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(ValueError, match="Snapshot directory not found"):
        IBKRBorrowDataFetcher(snapshot_dir=str(missing))


def test_snapshot_filename_convention(tmp_path: Path):
    (tmp_path / "borrow-state-AAPL-latest.json").write_text(
        '{"rate":"HIGH","availability":"AVAILABLE","changeDirection":"UP","timestamp":"2026-01-01T00:00:00Z"}'
    )

    fetcher = IBKRBorrowDataFetcher(snapshot_dir=str(tmp_path))
    data = fetcher.fetch_borrow_rates("AAPL", days=3)

    assert data["rate_bucket"] == "HIGH"
    assert data["borrow_rates"] == [10.0, 10.0, 10.0]


def test_fetch_ibkr_borrow_rates_convenience(tmp_path: Path):
    (tmp_path / "borrow-state-TSLA-latest.json").write_text(
        '{"rate":"LOW","availability":"AVAILABLE","changeDirection":"DOWN","timestamp":"2026-01-01T00:00:00Z"}'
    )

    data = fetch_ibkr_borrow_rates("TSLA", days=2, snapshot_dir=str(tmp_path))
    assert data["borrow_rates"] == [2.0, 2.0]


def test_raises_when_symbol_snapshot_missing(tmp_path: Path):
    fetcher = IBKRBorrowDataFetcher(snapshot_dir=str(tmp_path))
    with pytest.raises(ValueError, match="No borrow data available"):
        fetcher.fetch_borrow_rates("MSFT", days=5)
