# flow-state-monitor

A Python tool that monitors market flow states driven by forced buying pressure from short covering. It analyzes borrow-rate dynamics and price behavior to detect when non-optional buying pressure is active, weakening, or gone.

**This is NOT a trading signal, NOT predictive, and NOT a recommendation.** It simply monitors observable flow states to support disciplined exit decisions.

## Features

- **Borrow Rate Level Detection**: Identifies high borrow rates indicating forced buying pressure
- **Borrow Rate Delta Analysis**: Tracks daily changes in borrow rates (strengthening vs. weakening)
- **Borrow Rate Momentum**: Detects sustained trends in borrow rate changes over time
- **Price Spike Detection**: Identifies significant price movements consistent with forced buying
- **Abnormal Volatility Detection**: Flags unusual price volatility during covering events
- **Modular Design**: Each detection method is independent and can be used separately
- **Config-Driven**: Easily customize detection thresholds via YAML configuration
- **CLI Support**: Command-line interface for analyzing CSV data files
- **Ortex Integration**: Fetch borrow rate data directly from Ortex API
- **IBKR Integration**: Optional support for fetching price data from Interactive Brokers/CapTrader
- **Complete Solution**: Combine Ortex (borrow rates) + IBKR (prices) for fully automated data fetching
- **Flow State Output**: Returns ON / WEAKENING / OFF states (not trade signals)

## Installation

```bash
# Clone the repository
git clone https://github.com/hoppefamily/flow-state-monitor.git
cd flow-state-monitor

# Install in development mode
pip install -e .

# Optional: Install IBKR support for price data
pip install ib_insync

# Or install with dev dependencies for testing
pip install -e ".[dev]"
```

**Note**: Ortex integration requires no additional packages - just an API key!

## Quick Start

### Command Line

```bash
# Analyze data from CSV file
flow-state-monitor --csv examples/flow_on_example.csv

# Fetch borrow rates from Ortex + prices from CSV
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --price-csv prices.csv

# Fetch borrow rates from Ortex + prices from IBKR (COMPLETE SOLUTION!)
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --ibkr AAPL --days 30 --port 7497

# Use Ortex demo key for testing
flow-state-monitor --ortex AAPL --ortex-api-key TEST --price-csv prices.csv

# Legacy: Fetch prices from IBKR + borrow rates from CSV
flow-state-monitor --ibkr AAPL --days 30 --port 7497 --borrow-csv borrow_rates.csv

# Use custom configuration
flow-state-monitor --csv data.csv --config custom_config.yaml

# Get JSON output for scripting
flow-state-monitor --csv data.csv --json

# Specify custom column names
flow-state-monitor --csv data.csv --borrow-col borrow --price-col price
```

**Output example:**
```
============================================================
FLOW STATE MONITOR - ANALYSIS RESULTS
============================================================

⚠️  FLOW STATE: ON - Forced buying pressure is ACTIVE.
Borrow rate: 25.2% (HIGH). Pressure indicators suggest
ongoing short covering activity.

============================================================
```

**Exit codes:**
- 0 = OFF (no pressure)
- 1 = ON (pressure active)
- 2 = WEAKENING (pressure diminishing)
- 3 = error

### Python API

```python
from flow_state_monitor import FlowStateMonitor

# Sample data (most recent last)
borrow_rates = [2.5, 3.0, 5.2, 8.5, 11.2, 14.5, 17.8, 20.5]
prices = [100, 101.5, 107, 113, 118.5, 125, 132.5, 138]

# Create monitor and analyze
monitor = FlowStateMonitor()
results = monitor.analyze(borrow_rates, prices)

# Check flow state
print(f"Flow State: {results['flow_state']}")
print(f"Summary: {results['summary']}")

if results['flow_state'] == 'ON':
    print("⚠️  Forced buying pressure is active")
elif results['flow_state'] == 'WEAKENING':
    print("⚡ Forced buying pressure is weakening")
else:
    print("✓ No significant forced buying pressure")
```

## Usage Examples

### Basic Usage

```python
from flow_state_monitor import FlowStateMonitor

monitor = FlowStateMonitor()

# Minimum 6 data points required by default
borrow_rates = [2.0, 3.5, 5.0, 8.0, 12.0, 15.0, 18.0, 20.0]
prices = [100.0, 102.0, 105.0, 110.0, 117.0, 125.0, 132.0, 138.0]

results = monitor.analyze(borrow_rates, prices)
print(results['summary'])
```

### Custom Configuration

```python
from flow_state_monitor import Config, FlowStateMonitor

# Load custom config from YAML file
config = Config('custom_config.yaml')
monitor = FlowStateMonitor(config)

results = monitor.analyze(borrow_rates, prices)
```

Example config file (`custom_config.yaml`):

```yaml
borrow_level:
  high_threshold_percent: 15.0    # More conservative (default: 10.0)
  medium_threshold_percent: 8.0   # Higher medium threshold (default: 5.0)

borrow_momentum:
  lookback_period: 7              # Longer period (default: 5)
  positive_threshold_pct_points: 1.5  # Stronger momentum required (default: 1.0)

price_behavior:
  spike_threshold_percent: 7.0    # Larger spikes only (default: 5.0)
```

## Configuration Options

### Borrow Rate Level
- `high_threshold_percent`: Borrow rate % to indicate high pressure (default: 10.0%)
- `medium_threshold_percent`: Borrow rate % to indicate medium pressure (default: 5.0%)

### Borrow Rate Delta
- `increase_threshold_pct_points`: Daily increase to flag strengthening (default: 2.0 pct points)
- `decrease_threshold_pct_points`: Daily decrease to flag weakening (default: -2.0 pct points)

### Borrow Rate Momentum
- `lookback_period`: Days to analyze for momentum (default: 5)
- `positive_threshold_pct_points`: Avg daily increase to flag positive momentum (default: 1.0)
- `negative_threshold_pct_points`: Avg daily decrease to flag negative momentum (default: -1.0)

### Price Behavior
- `spike_threshold_percent`: Daily price increase % to flag spike (default: 5.0%)
- `volatility_lookback_period`: Days for volatility baseline (default: 20)
- `volatility_threshold_multiplier`: Multiplier for abnormal volatility (default: 2.0)

### General
- `min_data_points`: Minimum data points required (default: 6)

## Project Structure

```
flow-state-monitor/
├── src/
│   └── flow_state_monitor/
│       ├── __init__.py          # Package initialization
│       ├── monitor.py           # Main monitor class
│       ├── config.py            # Configuration management
│       ├── borrow_level.py      # Borrow rate level detection
│       ├── borrow_delta.py      # Borrow rate delta detection
│       ├── borrow_momentum.py   # Borrow rate momentum detection
│       ├── price_behavior.py    # Price spike and volatility detection
│       ├── ibkr_data.py         # Optional IBKR/CapTrader integration
│       ├── cli.py               # Command-line interface
│       └── __main__.py          # Module entry point
├── tests/                       # Test suite
│   ├── test_monitor.py
│   ├── test_borrow_level.py
│   ├── test_borrow_delta.py
│   ├── test_borrow_momentum.py
│   ├── test_price_behavior.py
│   ├── test_config.py
│   └── conftest.py
├── examples/                    # Usage examples
│   ├── ibkr_usage.py            # IBKR integration examples
│   ├── flow_on_example.csv
│   ├── flow_weakening_example.csv
│   └── flow_off_example.csv
├── config/
│   └── default_config.yaml      # Default configuration
├── pyproject.toml               # Package configuration
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── IBKR_QUICK_REFERENCE.md      # IBKR integration guide
├── PHILOSOPHY.md                # Design philosophy
└── LICENSE                      # GPL-3.0 license
```

## IBKR/CapTrader Integration

The flow-state-monitor optionally supports fetching price data from Interactive Brokers or CapTrader.

**Important**: IBKR only provides price data. Borrow rates must come from another source.

### Setup

```bash
# Install IBKR support
pip install ib_insync

# Start TWS or IB Gateway and enable API connections
```

### Python API

```python
from flow_state_monitor import FlowStateMonitor
from flow_state_monitor.ibkr_data import fetch_ibkr_data

# Fetch price data from IBKR
price_data = fetch_ibkr_data('AAPL', days=30, port=7497)

# Get borrow rates from your data source
borrow_rates = [2.5, 3.0, 5.2, 8.5, ...]  # Your broker/vendor

# Analyze
monitor = FlowStateMonitor()
results = monitor.analyze(
    borrow_rates=borrow_rates,
    prices=price_data['prices']
)
```

### Command Line

```bash
# Fetch prices from IBKR, borrow rates from CSV
flow-state-monitor --ibkr AAPL --days 30 --port 7497 --borrow-csv borrow.csv
```

See [IBKR_QUICK_REFERENCE.md](IBKR_QUICK_REFERENCE.md) for complete setup instructions and examples.

## Ortex Integration

The flow-state-monitor supports fetching borrow rate data from Ortex API. Combined with IBKR for prices, this provides a complete automated solution!

**Sign up**: https://public.ortex.com/
**Demo Key**: Use `TEST` for testing (limited data)

### Setup

No additional Python packages needed - just get an API key!

### Python API

```python
from flow_state_monitor import FlowStateMonitor
from flow_state_monitor.ortex_data import fetch_combined_data

# Fetch BOTH borrow rates (Ortex) and prices (IBKR) - complete solution!
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

### Or Fetch Only Borrow Rates

```python
from flow_state_monitor.ortex_data import fetch_ortex_borrow_rates

# Fetch borrow rates from Ortex
borrow_data = fetch_ortex_borrow_rates('AAPL', days=30, api_key='YOUR_KEY')

# Combine with your price data
monitor = FlowStateMonitor()
results = monitor.analyze(
    borrow_rates=borrow_data['borrow_rates'],
    prices=your_prices
)
```

### Command Line

```bash
# Complete solution: Ortex + IBKR
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --ibkr AAPL --days 30

# Ortex + CSV prices
flow-state-monitor --ortex AAPL --ortex-api-key YOUR_KEY --price-csv prices.csv

# Using demo key
flow-state-monitor --ortex AAPL --ortex-api-key TEST --price-csv prices.csv
```

See [ORTEX_QUICK_REFERENCE.md](ORTEX_QUICK_REFERENCE.md) for complete setup instructions and examples.

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=flow_state_monitor --cov-report=html

# Run specific test file
pytest tests/test_monitor.py
```

## How It Works

The monitor uses multiple signals to detect flow states:

1. **Borrow Rate Level**: Identifies when borrow rates are elevated (high/medium/low)

2. **Borrow Rate Delta**: Tracks daily changes - increasing rates suggest strengthening pressure, decreasing rates suggest weakening

3. **Borrow Rate Momentum**: Analyzes sustained trends over multiple days to identify directional pressure

4. **Price Spikes**: Detects significant upward price movements consistent with forced buying

5. **Abnormal Volatility**: Identifies unusual volatility patterns during covering events

**Flow State Logic**:
- **ON**: High/medium borrow rates + (positive momentum OR increasing delta OR price spike)
- **WEAKENING**: High/medium borrow rates + (negative momentum OR decreasing delta)
- **OFF**: Low borrow rates or no supporting pressure indicators

## Design Philosophy

- **Observable over Predictive**: Only describes current flow dynamics
- **Simple and Transparent**: Uses basic, well-understood metrics
- **Not a Trading System**: Monitors flow states, not entry/exit signals
- **Config-Driven**: Easy to adjust for different markets/instruments
- **No Data Included**: Users must provide their own borrow rate and price data
- **Modular**: Each component can be used independently

See [PHILOSOPHY.md](PHILOSOPHY.md) for detailed design philosophy.

## Important Disclaimers

⚠️ **This tool is for informational purposes only**

- NOT financial advice
- NOT a trading system
- NOT predictive of future prices
- Does NOT guarantee accuracy
- User assumes all risk

This tool monitors observable flow states. It cannot predict market direction or guarantee that detected conditions represent actual forced buying pressure.

## Data Sources

This project does not provide or redistribute market data. Users are responsible for:
- Obtaining borrow rate data from their broker or data provider
- Obtaining price data from authorized sources
- Ensuring compliance with data provider terms of service
- Understanding the accuracy and timeliness of their data

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This tool is inspired by the observation that forced buying pressure from short covering creates temporary, observable flow dynamics. It automates the monitoring of these dynamics rather than attempting to predict outcomes.
