# Relative Strength Analysis Feature

## Overview

The relative strength analysis feature automatically compares a stock's performance against major market benchmarks (SPY and QQQ) when using live data sources. This helps validate flow state signals by providing market context.

## When It's Available

**✅ Available:**
- Default mode: `flow-state-monitor AAPL` (Ortex + Alpaca)
- IBKR mode: `flow-state-monitor AAPL --use-ibkr` (Ortex + IBKR)

**❌ Not Available:**
- CSV mode: `flow-state-monitor --csv data.csv` (no symbol/fetcher)
- Price CSV mode: `flow-state-monitor AAPL --price-csv prices.csv` (no price fetcher for benchmarks)

## What It Shows

The analysis compares the stock's return against:

1. **SPY** - S&P 500 (broad market, 500 large-cap US stocks)
2. **QQQ** - Nasdaq-100 (tech-heavy, 100 largest non-financial Nasdaq stocks)

For each benchmark, you'll see:
- The stock's percentage return
- The benchmark's percentage return
- The relative performance (outperforming/underperforming)
- The magnitude of outperformance/underperformance

## Example Output

### Strong Signal (Outperforming)

```
============================================================
RELATIVE STRENGTH ANALYSIS
============================================================
INTL: +1.51% | vs SPY (+0.45%): outperforming by +1.06% | vs QQQ (-0.68%): outperforming by +2.19%
============================================================
```

**Interpretation:** Flow is ON and stock is outperforming both benchmarks → Strong signal

### Weak Signal (Underperforming)

```
============================================================
RELATIVE STRENGTH ANALYSIS
============================================================
AAPL: -4.29% | vs SPY (+0.45%): underperforming by -4.75% | vs QQQ (-0.68%): underperforming by -3.62%

⚠️  WARNING: Flow is ON but stock is underperforming SPY
    This may indicate a weak or false signal.

⚠️  WARNING: Flow is ON but stock is underperforming QQQ
    This may indicate a weak or false signal.
============================================================
```

**Interpretation:** Flow is ON but stock is underperforming both benchmarks → Potentially weak signal

## Signal Warnings

The system provides automatic warnings when flow state and relative strength diverge:

### Flow ON + Underperforming
- **Warning:** "Flow is ON but stock is underperforming [benchmark]"
- **Meaning:** Short covering may be active, but the stock isn't performing well relative to the market
- **Interpretation:** Could be a weak signal or false positive

### Flow OFF + Outperforming
- **Note:** "Flow is OFF but stock is outperforming [benchmark]"
- **Meaning:** No forced buying detected, but stock is performing better than market
- **Interpretation:** Stock may have momentum independent of short interest

## JSON Output

When using `--json`, relative strength data is included in structured format:

```json
{
  "flow_state": "ON",
  "relative_strength": {
    "stock_return": 1.51,
    "spy_return": 0.45,
    "qqq_return": -0.68,
    "spy_relative": 1.06,
    "qqq_relative": 2.19,
    "outperforming_spy": true,
    "outperforming_qqq": true,
    "description": "INTL: +1.51% | vs SPY (+0.45%): outperforming by +1.06% | vs QQQ (-0.68%): outperforming by +2.19%"
  }
}
```

## Implementation Details

### Why SPY and QQQ?

1. **Comprehensive Coverage:** SPY represents broad market (500 stocks), QQQ represents tech sector (100 stocks)
2. **No Guesswork:** Comparing to both benchmarks eliminates need to determine which index a stock belongs to
3. **Better Context:** Tech stocks can be compared to both general market and tech-specific performance

### Calculation Method

1. **Fetch Benchmark Data:** Retrieve SPY and QQQ prices for the same period as the stock
2. **Calculate Returns:**
   - Stock return = `(end_price - start_price) / start_price * 100`
   - Benchmark return = same calculation
3. **Compare:**
   - Relative performance = `stock_return - benchmark_return`
   - Outperforming if relative performance > 0

### Data Alignment

- Benchmark data is fetched for the same number of days as the stock
- Returns are calculated from the oldest to newest available data points
- If benchmark data is unavailable, analysis continues without it (non-critical)

## Use Cases

### 1. Validate Strong Signals

```bash
flow-state-monitor TSLA
```

If Flow is ON AND stock is outperforming → High confidence signal

### 2. Identify Weak Signals

```bash
flow-state-monitor XYZ
```

If Flow is ON BUT stock is underperforming → Low confidence signal (warnings shown)

### 3. Monitor Independent Momentum

```bash
flow-state-monitor NVDA
```

If Flow is OFF BUT stock is outperforming → Momentum may be from other factors

### 4. Automated Decision Making

```bash
result=$(flow-state-monitor AAPL --json)
flow_state=$(echo $result | jq -r '.flow_state')
outperforming_spy=$(echo $result | jq -r '.relative_strength.outperforming_spy')

if [[ "$flow_state" == "ON" && "$outperforming_spy" == "true" ]]; then
    echo "Strong signal - flow ON and outperforming market"
else
    echo "Weak or mixed signal"
fi
```

## Configuration

No configuration is required - relative strength analysis is automatic when using live data sources.

To disable or modify, you would need to:
1. Edit the CLI to skip the benchmark fetching section
2. Or use CSV/price-csv modes which naturally exclude this feature

## Performance Impact

- **Additional API Calls:** 2 extra API calls (SPY and QQQ) to Alpaca/IBKR
- **Additional Time:** ~1-2 seconds for benchmark data fetch
- **Error Handling:** If benchmark fetch fails, analysis continues without relative strength (non-critical)

## Future Enhancements

Possible future improvements:
- Add DIA (Dow Jones) as third benchmark
- Allow custom benchmark symbols via CLI argument
- Add sector-specific benchmarks (XLK for tech, XLF for financials, etc.)
- Support relative strength in CSV mode with separate benchmark CSV files
- Add relative strength charts/visualization
