"""Shared test fixtures for flow state monitor tests."""

import pytest


@pytest.fixture
def sample_borrow_rates_stable():
    """Stable low borrow rates."""
    return [1.0, 1.2, 1.1, 1.3, 1.2, 1.4, 1.3, 1.2]


@pytest.fixture
def sample_borrow_rates_increasing():
    """Increasing borrow rates indicating rising pressure."""
    return [2.0, 4.0, 6.5, 9.0, 12.5, 16.0, 19.5, 22.0]


@pytest.fixture
def sample_borrow_rates_decreasing():
    """Decreasing borrow rates indicating weakening pressure."""
    return [20.0, 18.5, 16.0, 14.5, 12.0, 10.5, 9.0, 8.0]


@pytest.fixture
def sample_prices_stable():
    """Stable prices with small variations."""
    return [100.0, 100.5, 99.8, 100.2, 99.9, 100.3, 100.1, 100.0]


@pytest.fixture
def sample_prices_spiking():
    """Prices with significant upward movement."""
    return [100.0, 102.0, 105.0, 110.0, 117.0, 125.0, 132.0, 138.0]


@pytest.fixture
def sample_prices_declining():
    """Declining prices."""
    return [145.0, 143.5, 142.0, 141.0, 140.5, 140.2, 139.8, 139.5]
