"""Tests for main monitor module."""

import pytest
from flow_state_monitor import FlowStateMonitor, Config


def test_monitor_initialization():
    """Test monitor initializes correctly."""
    monitor = FlowStateMonitor()
    
    assert monitor.config is not None


def test_analyze_flow_state_on(sample_borrow_rates_increasing, sample_prices_spiking):
    """Test detection of ON flow state."""
    monitor = FlowStateMonitor()
    results = monitor.analyze(sample_borrow_rates_increasing, sample_prices_spiking)
    
    assert results['flow_state'] == 'ON'
    assert 'borrow_level' in results['signals']
    assert 'borrow_delta' in results['signals']
    assert 'borrow_momentum' in results['signals']
    assert 'price_spike' in results['signals']


def test_analyze_flow_state_weakening(sample_borrow_rates_decreasing, sample_prices_declining):
    """Test detection of WEAKENING flow state."""
    monitor = FlowStateMonitor()
    results = monitor.analyze(sample_borrow_rates_decreasing, sample_prices_declining)
    
    assert results['flow_state'] == 'WEAKENING'


def test_analyze_flow_state_off(sample_borrow_rates_stable, sample_prices_stable):
    """Test detection of OFF flow state."""
    monitor = FlowStateMonitor()
    results = monitor.analyze(sample_borrow_rates_stable, sample_prices_stable)
    
    assert results['flow_state'] == 'OFF'


def test_analyze_returns_all_fields():
    """Test that analyze returns all required fields."""
    borrow_rates = [5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0]
    prices = [100.0, 102.0, 105.0, 108.0, 112.0, 117.0, 123.0, 130.0]
    
    monitor = FlowStateMonitor()
    results = monitor.analyze(borrow_rates, prices)
    
    assert 'flow_state' in results
    assert 'signals' in results
    assert 'summary' in results
    assert isinstance(results['flow_state'], str)
    assert isinstance(results['signals'], dict)
    assert isinstance(results['summary'], str)


def test_analyze_insufficient_borrow_rates():
    """Test that insufficient borrow rate data raises ValueError."""
    borrow_rates = [5.0, 7.0]  # Only 2 points
    prices = [100.0, 102.0, 104.0, 106.0, 108.0, 110.0]
    
    monitor = FlowStateMonitor()
    
    with pytest.raises(ValueError, match="at least"):
        monitor.analyze(borrow_rates, prices)


def test_analyze_insufficient_prices():
    """Test that insufficient price data raises ValueError."""
    borrow_rates = [5.0, 7.0, 9.0, 11.0, 13.0, 15.0]
    prices = [100.0, 102.0]  # Only 2 points
    
    monitor = FlowStateMonitor()
    
    with pytest.raises(ValueError, match="at least"):
        monitor.analyze(borrow_rates, prices)


def test_monitor_with_custom_config():
    """Test monitor with custom configuration."""
    config = Config()
    monitor = FlowStateMonitor(config)
    
    borrow_rates = [5.0, 7.0, 9.0, 11.0, 13.0, 15.0]
    prices = [100.0, 102.0, 104.0, 106.0, 108.0, 110.0]
    
    results = monitor.analyze(borrow_rates, prices)
    
    assert 'flow_state' in results


def test_signal_details_structure():
    """Test that signal details have expected structure."""
    borrow_rates = [5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0]
    prices = [100.0, 102.0, 105.0, 108.0, 112.0, 117.0, 123.0, 130.0]
    
    monitor = FlowStateMonitor()
    results = monitor.analyze(borrow_rates, prices)
    
    # Check borrow level signal structure
    assert 'borrow_level' in results['signals']
    level_signal = results['signals']['borrow_level']
    assert 'level' in level_signal
    assert 'details' in level_signal or 'error' in level_signal
    
    # Check borrow delta signal structure
    assert 'borrow_delta' in results['signals']
    delta_signal = results['signals']['borrow_delta']
    assert 'change_type' in delta_signal
    
    # Check momentum signal structure
    assert 'borrow_momentum' in results['signals']
    momentum_signal = results['signals']['borrow_momentum']
    assert 'momentum_type' in momentum_signal


def test_summary_contains_flow_state():
    """Test that summary mentions the flow state."""
    borrow_rates = [1.0, 1.2, 1.3, 1.4, 1.5, 1.6]
    prices = [100.0, 100.5, 101.0, 101.5, 102.0, 102.5]
    
    monitor = FlowStateMonitor()
    results = monitor.analyze(borrow_rates, prices)
    
    summary = results['summary'].upper()
    assert results['flow_state'] in summary
