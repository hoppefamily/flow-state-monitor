# Ortex Integration - Quick Reference

## Overview

Ortex provides borrow rate and short interest data. Combined with IBKR price data, this gives you everything needed for complete flow state monitoring.

## Installation

```bash
# Core package (no extra dependencies needed for Ortex)
pip install -e .

# Optional: For complete solution with IBKR prices
pip install ib_insync
```

## Setup

1. Sign up at https://public.ortex.com/
2. Get your API key from account settings
3. Use `TEST` for demo/testing (limited data)

## Quick Start

### Fetch Borrow Rates Only

```python
from flow_state_monitor.ortex_data import fetch_ortex_borrow_rates

# Using demo key
borrow_data = fetch_ortex_borrow_rates('AAPL', days=30, api_key='TEST')
# Returns: {'borrow_rates': [2.5, 3.0, 5.2, ...]}
```

### Complete Analysis with IBKR Prices

```python
from flow_state_monitor.ortex_data import fetch_combined_data
from flow_state_monitor import FlowStateMonitor

# Fetch both borrow rates and prices
data = fetch_combined_data(
    symbol='AAPL',
    days=30,
    ortex_api_key='YOUR_KEY',  # or 'TEST' for demo
    ibkr_port=7497
)

# Analyze
monitor = FlowStateMonitor()
results = monitor.analyze(**data)
print(results['summary'])
```

### With Your Own Price Data

```python
from flow_state_monitor.ortex_data import fetch_ortex_borrow_rates
from flow_state_monitor import FlowStateMonitor

# Fetch borrow rates
borrow_data = fetch_ortex_borrow_rates('AAPL', days=30, api_key='YOUR_KEY')

# Load your prices from wherever
prices = [150.0, 152.5, 155.0, ...]  # Your price source

# Analyze
monitor = FlowStateMonitor()
results = monitor.analyze(
    borrow_rates=borrow_data['borrow_rates'],
    prices=prices
)
```

## Command Line Usage

### Ortex + CSV Prices

```bash
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --price-csv prices.csv
```

### Ortex + IBKR (Complete Solution!)

```bash
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --ibkr AAPL --days 30 --port 7497
```

### Using Demo Key

```bash
flow-state-monitor --ortex AAPL --ortex-api-key TEST --price-csv prices.csv
```

### JSON Output

```bash
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --price-csv prices.csv --json
```

## Data Combinations

| Borrow Rates | Prices | Command |
|--------------|--------|---------|
| CSV | CSV | `--csv data.csv` |
| Ortex | CSV | `--ortex SYMBOL --price-csv prices.csv` |
| CSV | IBKR | `--ibkr SYMBOL --borrow-csv borrow.csv` |
| **Ortex** | **IBKR** | `--ortex SYMBOL --ibkr SYMBOL` ✨ |

## API Key Management

### Demo/Test Key

```bash
# Use 'TEST' for demonstration
export ORTEX_API_KEY='TEST'
flow-state-monitor --ortex AAPL --ortex-api-key $ORTEX_API_KEY --price-csv prices.csv
```

### Production Key

```bash
# Set your real API key
export ORTEX_API_KEY='your-real-key-here'
flow-state-monitor --ortex AAPL --ortex-api-key $ORTEX_API_KEY --ibkr AAPL
```

## Common Issues

### Authentication Failed

```
ConnectionError: Ortex API authentication failed
```

**Solutions:**
1. Check your API key is correct
2. Use 'TEST' for demo access
3. Verify your account is active
4. Check API key permissions in Ortex dashboard

### Rate Limit Exceeded

```
ConnectionError: Ortex API rate limit exceeded
```

**Solutions:**
1. Wait a moment before retrying
2. Reduce frequency of requests
3. Upgrade your Ortex API plan
4. Cache results locally

### Symbol Not Found

```
ValueError: No borrow rate data available for XYZ
```

**Solutions:**
1. Verify symbol spelling (must be uppercase)
2. Check if Ortex tracks this symbol
3. Try a more common symbol first (AAPL, TSLA, etc.)
4. Adjust date range (some symbols have limited history)

### Connection Error

```
ConnectionError: Failed to connect to Ortex API
```

**Solutions:**
1. Check internet connection
2. Verify Ortex API is accessible (check status page)
3. Check firewall/proxy settings
4. Try again later if Ortex is experiencing issues

## Python API Examples

### Using Fetcher Class

```python
from flow_state_monitor.ortex_data import OrtexDataFetcher

fetcher = OrtexDataFetcher(api_key='YOUR_KEY')

# Fetch borrow rates
data = fetcher.fetch_borrow_rates('AAPL', days=30)
print(f"Latest rate: {data['borrow_rates'][-1]}%")

# Fetch comprehensive short interest
short_data = fetcher.fetch_short_interest('AAPL', days=30)
# Returns detailed metrics
```

### Multiple Symbols

```python
from flow_state_monitor.ortex_data import OrtexDataFetcher

fetcher = OrtexDataFetcher(api_key='YOUR_KEY')
symbols = ['AAPL', 'TSLA', 'GME', 'AMC']

for symbol in symbols:
    try:
        data = fetcher.fetch_borrow_rates(symbol, days=10)
        print(f"{symbol}: {data['borrow_rates'][-1]:.2f}%")
    except Exception as e:
        print(f"{symbol}: Error - {e}")
```

### Error Handling

```python
from flow_state_monitor.ortex_data import fetch_ortex_borrow_rates

try:
    data = fetch_ortex_borrow_rates('AAPL', api_key='YOUR_KEY')
except ConnectionError as e:
    print(f"API Error: {e}")
except ValueError as e:
    print(f"Data Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
```

## Pricing & Limits

- **Free Tier**: Limited API calls, demo key 'TEST' available
- **Paid Tiers**: Higher rate limits, more symbols, real-time data
- Check https://public.ortex.com/ for current pricing

## Data Fields

Ortex provides:
- **borrow_rate**: Cost to borrow shares (percentage)
- **short_interest**: Total shares sold short
- **utilization**: Percentage of available shares on loan
- **days_to_cover**: Estimated days to cover short positions
- And more...

For flow-state-monitor, we primarily use **borrow_rate**.

## Best Practices

1. **Cache Results**: Store fetched data to avoid repeated API calls
2. **Error Handling**: Always wrap API calls in try/except blocks
3. **Rate Limiting**: Respect API limits, add delays between requests
4. **Data Validation**: Check data length and values before analysis
5. **API Key Security**: Never commit API keys to version control

## Complete Workflow Example

```python
from flow_state_monitor import FlowStateMonitor, Config
from flow_state_monitor.ortex_data import fetch_combined_data

# Optional: Custom configuration
config = Config()  # or Config('custom_config.yaml')

# Fetch data from both sources
data = fetch_combined_data(
    symbol='AAPL',
    days=30,
    ortex_api_key='YOUR_KEY',
    ibkr_port=7497
)

# Analyze
monitor = FlowStateMonitor(config)
results = monitor.analyze(**data)

# Check flow state
if results['flow_state'] == 'ON':
    print("⚠️  Forced buying pressure is ACTIVE")
    print(f"Borrow rate: {data['borrow_rates'][-1]:.2f}%")
elif results['flow_state'] == 'WEAKENING':
    print("⚡ Pressure is weakening")
else:
    print("✓ No significant pressure")

print(f"\n{results['summary']}")
```

## See Also

- `examples/ortex_usage.py` - Complete code examples
- `IBKR_QUICK_REFERENCE.md` - IBKR price data integration
- README.md - General usage information
- Ortex API Docs: https://public.ortex.com/api-docs
