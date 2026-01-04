# Ortex Integration - Quick Reference

## Overview

Ortex provides borrow rate and short interest data. Combined with Alpaca price data (or IBKR), this gives you everything needed for complete flow state monitoring with automatic relative strength analysis against SPY and QQQ benchmarks.

## Installation

```bash
# Core package (no extra dependencies needed for Ortex)
pip install -e .

# Recommended: For complete solution with Alpaca prices
pip install alpaca-py

# Alternative: For IBKR prices instead
pip install ib_insync
```

## Setup

1. Sign up at https://public.ortex.com/
2. Get your API key from account settings
3. Set environment variable: `export ORTEX_API_KEY=your_key_here`
4. Set Alpaca credentials: `export ALPACA_API_KEY=...` and `export ALPACA_SECRET_KEY=...`
5. Use `TEST` for demo/testing (limited data)

## Quick Start

### Environment Setup (Recommended)

```bash
# Set environment variables
export ORTEX_API_KEY=your_api_key_here
export ALPACA_API_KEY=your_alpaca_key
export ALPACA_SECRET_KEY=your_alpaca_secret

# Or create .env file
cat > .env << EOF
ORTEX_API_KEY=your_api_key_here
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
EOF
```

### Fetch Borrow Rates Only

```python
from flow_state_monitor.ortex_data import fetch_ortex_borrow_rates

# Using demo key
borrow_data = fetch_ortex_borrow_rates('AAPL', days=30, api_key='TEST')
# Returns: {'borrow_rates': [2.5, 3.0, 5.2, ...]}
```

### Complete Analysis with Alpaca Prices (Recommended)

```python
from flow_state_monitor.alpaca_data import fetch_combined_data
from flow_state_monitor import FlowStateMonitor

# Fetch both borrow rates from Ortex and prices from Alpaca
data = fetch_combined_data(
    symbol='AAPL',
    days=30,
    ortex_api_key='YOUR_KEY',  # or 'TEST' for demo
    alpaca_api_key='YOUR_ALPACA_KEY',
    alpaca_secret_key='YOUR_ALPACA_SECRET'
)

# Analyze
monitor = FlowStateMonitor()
results = monitor.analyze(**data)
print(results['summary'])
```

### Alternative: With IBKR Prices

```python
from flow_state_monitor.ibkr_data import fetch_combined_data
from flow_state_monitor import FlowStateMonitor

# Fetch both borrow rates and prices
data = fetch_combined_data(
    symbol='AAPL',
    days=30,
    ortex_api_key='YOUR_KEY',
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

### Default Mode (Ortex + Alpaca)

```bash
# Uses ORTEX_API_KEY, ALPACA_API_KEY, and ALPACA_SECRET_KEY from environment
# Automatically includes relative strength analysis against SPY and QQQ
flow-state-monitor AAPL

# With explicit days
flow-state-monitor AAPL --days 30

# Output includes:
# - Flow state analysis (ON/OFF/WEAKENING)
# - Relative strength vs SPY (S&P 500)
# - Relative strength vs QQQ (Nasdaq-100)
# - Warnings if flow is ON but stock underperforms benchmarks
```

### Ortex + CSV Prices

```bash
# Uses ORTEX_API_KEY from environment
flow-state-monitor AAPL --price-csv prices.csv

# Override API key
flow-state-monitor AAPL --ortex-api-key YOUR_KEY --price-csv prices.csv
```

### Using IBKR Instead of Alpaca

```bash
# Uses ORTEX_API_KEY from environment, IBKR for prices
flow-state-monitor AAPL --use-ibkr
```

### Using Demo Key

```bash
flow-state-monitor AAPL --ortex-api-key TEST --price-csv prices.csv
```

### JSON Output

```bash
flow-state-monitor AAPL --json
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
