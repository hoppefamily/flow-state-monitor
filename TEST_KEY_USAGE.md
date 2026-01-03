# Testing with the TEST API Key

The Ortex integration now supports a **TEST mode** for demo and testing purposes!

## How It Works

When you use `TEST` as the API key, the module returns **simulated borrow rate data** instead of making actual API calls. This allows you to:

- Test the integration without needing a real Ortex API key
- Develop and debug your workflows
- Understand the data format and analysis output
- Create demos and examples

## Quick Test

```bash
# Test with simulated Ortex data + sample prices
cd /Users/michaelhoppe/code/flow-state-monitor/examples
flow-state-monitor --ortex AAPL --ortex-api-key TEST --price-csv sample_prices.csv
```

## What Gets Simulated

The TEST key generates:
- **Borrow rates**: Random but realistic rates (1.5% - 8%) with some volatility
- **Consistent per symbol**: Same symbol always gets the same base rate (deterministic)
- **Proper format**: Returns data in the exact format the real API would use

## Example Output

```
✓ FLOW STATE: OFF - No significant forced buying pressure detected.
  Borrow rate: 3.9% (LOW). Market flow appears normal.

SIGNAL DETAILS:
• BORROW RATE LEVEL: LOW (3.93%)
• BORROW RATE CHANGE: STABLE
• BORROW RATE MOMENTUM: NEUTRAL
• PRICE SPIKE DETECTED: NO
• ABNORMAL VOLATILITY: NO
```

## Moving to Production

When you're ready to use real data:

1. Sign up at https://public.ortex.com/
2. Get your API key
3. Replace TEST with your real key:

```bash
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_REAL_KEY --price-csv prices.csv

# Or combine with IBKR for full automation:
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_REAL_KEY --ibkr AAPL
```

## Python API

The TEST mode also works with the Python API:

```python
from flow_state_monitor.ortex_data import fetch_ortex_borrow_rates

# Returns simulated data
data = fetch_ortex_borrow_rates('AAPL', days=30, api_key='TEST')
print(data['borrow_rates'])  # [8.85, 8.54, 7.47, ...]
```

## Connection Test

Run the connection test to verify everything is working:

```bash
python check_ortex_connection.py
```

This will test:
- Module imports
- TEST key demo data
- CLI integration

---

**Note**: The TEST key is for testing the integration only. For real trading decisions, always use a real Ortex API key to get actual market data.
