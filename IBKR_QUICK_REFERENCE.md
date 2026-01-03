# IBKR Integration - Quick Reference

## Installation

```bash
# Core package
pip install -e .

# Optional IBKR support
pip install ib_insync
```

## Setup Checklist

- [ ] Install `ib_insync`
- [ ] Start TWS or IB Gateway
- [ ] Login to IBKR account (paper or live)
- [ ] Enable API in settings (File → Global Configuration → API → Settings)
- [ ] Check "Enable ActiveX and Socket Clients"
- [ ] Note your port number (7497 for TWS paper trading)
- [ ] Test connection with: `python -c "from flow_state_monitor.ibkr_data import fetch_ibkr_data; print('OK')"`

## Quick Start

### Important Note

**IBKR only provides price data.** You must obtain borrow rates from another source such as:
- Your broker's API or website
- A data vendor (e.g., S3 Partners, Ortex)
- Manual tracking

### One-Line Price Fetch

```python
from flow_state_monitor.ibkr_data import fetch_ibkr_data

price_data = fetch_ibkr_data('AAPL', days=30, port=7497)
# Returns: {'prices': [...], 'opens': [...], 'highs': [...], 'lows': [...]}
```

### Complete Analysis with Borrow Rates

```python
from flow_state_monitor import FlowStateMonitor
from flow_state_monitor.ibkr_data import fetch_ibkr_data

# Fetch price data from IBKR
price_data = fetch_ibkr_data('AAPL', days=30, port=7497)

# Get borrow rates from your data source
borrow_rates = [2.5, 3.0, 5.2, 8.5, 11.2, ...]  # Your data source

# Analyze
monitor = FlowStateMonitor()
results = monitor.analyze(
    borrow_rates=borrow_rates,
    prices=price_data['prices']
)
```

### Using Context Manager

```python
from flow_state_monitor.ibkr_data import IBKRDataFetcher

with IBKRDataFetcher(port=7497) as fetcher:
    # Fetch data for multiple symbols
    symbols_data = fetcher.fetch_multiple_symbols(['AAPL', 'MSFT', 'GOOGL'])

    for symbol, data in symbols_data.items():
        if data:
            print(f"{symbol}: {data['prices'][-1]}")
```

## Command Line Usage

```bash
# Fetch price data from IBKR and combine with borrow rates from CSV
flow-state-monitor --ibkr AAPL --days 30 --port 7497 --borrow-csv borrow_rates.csv

# Paper trading (port 7497)
flow-state-monitor --ibkr TSLA --days 20 --port 7497 --borrow-csv borrow.csv

# Live trading (port 7496) - use with caution
flow-state-monitor --ibkr SPY --days 30 --port 7496 --borrow-csv borrow.csv

# JSON output for scripting
flow-state-monitor --ibkr AAPL --borrow-csv borrow.csv --json
```

## Port Numbers

| Environment | Application | Port |
|-------------|-------------|------|
| Paper Trading | TWS | 7497 |
| Live Trading | TWS | 7496 |
| Paper Trading | IB Gateway | 4002 |
| Live Trading | IB Gateway | 4001 |

## Common Issues

### Connection Refused

```
ConnectionError: Failed to connect to IBKR at 127.0.0.1:7497
```

**Solutions:**
1. Start TWS or IB Gateway
2. Check API is enabled in settings
3. Verify correct port number
4. Check firewall settings

### Import Error

```
ImportError: ib_insync library is required
```

**Solution:**
```bash
pip install ib_insync
```

### Symbol Not Found

```
ValueError: Could not find contract for symbol 'XYZ'
```

**Solutions:**
1. Check symbol spelling
2. Try specifying exchange: `fetch_daily_bars('AAPL', exchange='NASDAQ')`
3. Verify symbol has trading data for requested period

### Data Length Mismatch

When combining IBKR price data with borrow rates from another source, ensure both have the same number of data points. The CLI will automatically align to the shorter length and warn you.

## Examples

See `examples/ibkr_usage.py` for complete working examples:
- Simple data fetch
- Context manager usage
- Manual connection management
- Custom configuration

## Getting Borrow Rate Data

Since IBKR doesn't provide borrow rates through their API, you'll need to:

1. **Manual tracking**: Export borrow rates from your broker daily
2. **Broker API**: Use your broker's API if they provide borrow rate data
3. **Data vendors**: Subscribe to services like:
   - S3 Partners
   - Ortex
   - IHS Markit
4. **CSV files**: Maintain a CSV file with date and borrow_rate columns

Example CSV format:
```csv
date,borrow_rate
2025-01-01,2.5
2025-01-02,3.0
2025-01-03,5.2
```

## See Also

- `examples/ibkr_usage.py` - Complete code examples
- IBKR API documentation: https://interactivebrokers.github.io/tws-api/
- ib_insync documentation: https://ib-insync.readthedocs.io/
