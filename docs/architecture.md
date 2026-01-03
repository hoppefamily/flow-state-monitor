# Architecture Documentation

## Summary

The flow-state-monitor has been successfully updated to implement all requirements from the design specification (see [design_specification.md](design_specification.md)):

## ✓ Implemented Features

### 1. Market State Detection
- **market_state**: Detects elastic (OFF) vs constrained (ON) market conditions
- Implemented in: `src/flow_state_monitor/market_state.py`
- Threshold: 5% borrow rate (configurable)

### 2. Flow State Detection
- **flow_state**: Detects forced buying pressure (ON/WEAKENING/OFF)
- Based on borrow rate level, momentum, and price behavior
- Existing implementation enhanced

### 3. EMA-Based Momentum
- Replaced simple average with **EMA of daily deltas**: `EMA(ΔB)`
- Configurable span: default 3, can use 5
- Implemented in: `src/flow_state_monitor/borrow_momentum.py`
- Formula: `ΔB(t) = borrow_rate(t) - borrow_rate(t-1)`

### 4. Signal Generation (BUY/SELL/HOLD)
- **BUY Signal**: When both market_state and flow_state flip from OFF to ON within 0-1 trading days
- **SELL Signal**: When `EMA(ΔB) < -epsilon` for 1+ trading day (constraint exhaustion)
- **HOLD Signal**: No transition detected
- Implemented in: `src/flow_state_monitor/signals.py`
- Tracks state transitions across time

### 5. Output Format (per Design Specification)
- market_state (ON/OFF)
- flow_state (ON/WEAKENING/OFF)
- borrow_rate level
- borrow_rate delta
- smoothed borrow momentum (EMA)
- explicit reason for BUY / SELL / HOLD
- Human-readable format

### 6. Configuration
- All thresholds configurable via YAML
- New parameters added:
  - `borrow_momentum.ema_span`: EMA span (default: 3)
  - `market_state.tension_threshold_percent`: Market state threshold (default: 5.0%)
  - `signals.epsilon`: Exit signal deadband (default: 0.05)
  - `signals.exit_confirmation_days`: Confirmation period (default: 1)

## File Changes

### New Files
1. `src/flow_state_monitor/market_state.py` - Market state detection
2. `src/flow_state_monitor/signals.py` - Signal generation with state tracking
3. `examples/copilot_spec_demo.py` - Comprehensive demonstration
4. `test_copilot_spec.py` - Test script for implementation
5. `test_buy_signal.py` - BUY signal specific test

### Modified Files
1. `src/flow_state_monitor/borrow_momentum.py` - Added EMA calculation
2. `src/flow_state_monitor/monitor.py` - Integrated all new features
3. `src/flow_state_monitor/config.py` - Added new configuration sections
4. `src/flow_state_monitor/cli.py` - Updated output format
5. `config/default_config.yaml` - Added new parameters

## Usage Examples

### Python API

```python
from flow_state_monitor import FlowStateMonitor

monitor = FlowStateMonitor()

result = monitor.analyze(
    borrow_rates=[2.0, 3.0, 6.5, 11.0, ...],
    prices=[100, 101, 107, 115, ...]
)

print(result['market_state'])   # ON or OFF
print(result['flow_state'])     # ON, WEAKENING, or OFF
print(result['signal'])         # BUY, SELL, or HOLD
print(result['signal_reason'])  # Explanation
print(result['summary'])        # Full formatted output
```

### CLI

```bash
# With Ortex API (live data)
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --ibkr AAPL

# With CSV files
flow-state-monitor --borrow-csv borrow.csv --price-csv prices.csv

# With TEST demo key
flow-state-monitor --ortex AAPL --ortex-api-key TEST --price-csv prices.csv
```

### Output Example

```
============================================================
FLOW STATE MONITOR - ANALYSIS
============================================================

MARKET STATE: ON
  → Elasticity broken - structural tension exists

FLOW STATE: ON
  → Forced buying pressure ACTIVE

BORROW RATE METRICS:
  • Level: 16.00% (HIGH)
  • Delta: -0.80 pct points
  • Smoothed Momentum (EMA-3): -0.544 pct points/day

🔴 SIGNAL: SELL
  Reason: EXIT: Borrow momentum -0.544 < -epsilon (-0.050)
  for 1+ day - constraint exhaustion detected

============================================================
```

## Testing

Run the demonstration:
```bash
python examples/copilot_spec_demo.py
```

Run specific tests:
```bash
python test_copilot_spec.py     # Full test suite
python test_buy_signal.py       # BUY signal test
```

## Key Design Principles (per COPILOT_SPEC.md)

✓ **Deterministic logic only** - No ML, no forecasting, no prediction
✓ **All thresholds configurable** - Defaults are conservative
✓ **Constraint transition detection** - Not price-based
✓ **Noise handling** - EMA smoothing, deadband (epsilon), confirmation period
✓ **Explainable** - Clear reasons for every signal
✓ **Reproducible** - Same inputs always produce same outputs

## Exit Strategy

Important: Per the design specification, exit is:
- **NOT** price-based
- **NOT** flow_state-based
- **NOT** waiting for price reversal
- **IS** based on borrow rate momentum exhaustion only

Exit when: `EMA(ΔB) < -epsilon` for 1+ day

This detects constraint exhaustion earlier than price-based exits.

## Notes

- Signal generator maintains state history across calls
- First analysis after initialization shows "Insufficient history"
- Minimum 6 data points required for analysis
- Signal requires 2+ days for proper state transition tracking

## Next Steps

The implementation is complete and tested. All COPILOT_SPEC.md requirements have been met:

1. ✓ market_state detection (ON/OFF)
2. ✓ flow_state detection (ON/WEAKENING/OFF)
3. ✓ EMA-based momentum
4. ✓ BUY signal on state transitions
5. ✓ SELL signal on momentum exhaustion
6. ✓ HOLD signal default
7. ✓ Output format per spec
8. ✓ Deterministic and configurable
9. ✓ Human-readable explanations

Ready for use!
