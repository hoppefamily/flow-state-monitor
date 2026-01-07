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
- **IBKR Borrow Sensor Integration**: Fetch borrow rate data from IBKR Borrow Sensor snapshot files
- **Alpaca Integration**: Fetch price data from Alpaca Markets (default, easier than IBKR)
- **IBKR Integration**: Optional support for fetching price data from Interactive Brokers/CapTrader
- **Complete Solution**: Combine IBKR Borrow Sensor (borrow rates) + Alpaca (prices) for fully automated data fetching
- **Relative Strength Analysis**: Compare stock performance against SPY and QQQ benchmarks to validate signals
- **Flow State Output**: Returns ON / WEAKENING / OFF states (not trade signals)

## Understanding the Tool's Domain

flow-state-monitor operates in the **Money Flow Domain** - it detects price movements driven by mechanical constraints (short covering pressure). It works best for stocks with significant short interest and rising borrow rates.

**When flow-state-monitor shows limitations:**
- Stocks with major narrative events (leadership changes, strategic pivots)
- Low short interest stocks with big moves
- Sentiment-driven volatility

**Example:** Berkshire Hathaway (BRK.B) during Buffett succession discussions shows Flow OFF (correct - no shorts) but underperforms due to narrative uncertainty. This is outside the money flow domain.

📖 **See [Money Flow vs Narrative Flow](docs/money_flow_vs_narrative.md) for detailed explanation of when to use this tool vs. narrative analysis tools.**

## Installation

### As a Package (For Consumers)

**This is a private repo.** The recommended install method is via git (pinned to a tag):

```bash
# Recommended: install a tagged version
pip install "flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0"

# Development only: track main
pip install "flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@main"
```

📖 See [PACKAGE_INSTALLATION.md](PACKAGE_INSTALLATION.md) for `requirements.txt` and CI/CD examples.

### For Development

```bash
# Clone the repository
git clone https://github.com/hoppefamily/flow-state-monitor.git
cd flow-state-monitor

# Create and activate virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .

# Install Alpaca support for price data (recommended)
pip install alpaca-py

# Optional: Install IBKR support for price data (alternative)
pip install ib_insync

# Or install with dev dependencies for testing
pip install -e ".[dev]"
```

**Note**: IBKR Borrow Sensor integration reads JSON snapshots from local files - no API key needed!
**Note**: Alpaca is the recommended price data source (easier setup than IBKR).

## Quick Start

### Environment Setup

Create a `.env` file or set environment variables:

```bash
# IBKR Borrow Sensor snapshot directory (default: ./output)
export IBKR_SNAPSHOT_DIR=./output

# Alpaca API credentials (get free keys from https://alpaca.markets/)
export ALPACA_API_KEY=your_alpaca_key
export ALPACA_SECRET_KEY=your_alpaca_secret

# Optional: IBKR configuration (only if using --use-ibkr for price data)
export IBKR_PORT=7497
export IBKR_HOST=127.0.0.1
```

See [.env.example](.env.example) for a template.

### Command Line

```bash
# Default mode: Fetch from IBKR Borrow Sensor + Alpaca (easiest!)
flow-state-monitor AAPL

# With explicit days parameter
flow-state-monitor AAPL --days 30

# Use IBKR instead of Alpaca for prices
flow-state-monitor AAPL --use-ibkr

# Analyze data from CSV file
flow-state-monitor --csv examples/flow_on_example.csv

# Fetch borrow rates from IBKR Borrow Sensor + prices from CSV (no relative strength)
flow-state-monitor AAPL --price-csv prices.csv

# Specify custom snapshot directory
flow-state-monitor AAPL --ibkr-snapshot-dir /path/to/snapshots

# Override API keys from environment
flow-state-monitor AAPL --alpaca-api-key YOUR_KEY --alpaca-secret-key YOUR_SECRET

# Use custom configuration
flow-state-monitor AAPL --config custom_config.yaml

# Get JSON output for scripting
flow-state-monitor AAPL --json

# Specify custom column names (for CSV mode)
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

============================================================
RELATIVE STRENGTH ANALYSIS
============================================================
AAPL: +15.25% | vs SPY (+8.45%): outperforming by +6.80% | vs QQQ (+10.22%): outperforming by +5.03%
============================================================
```

**Note**: When using live data sources (IBKR Borrow Sensor + Alpaca/IBKR), relative strength analysis is automatically included. It compares the stock's performance against SPY (S&P 500) and QQQ (Nasdaq-100) benchmarks to help validate the flow signal. A strong flow signal with underperformance vs benchmarks may indicate a weak or false signal. Relative strength is not available when using CSV files for price data.

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

## IBKR Borrow Sensor Integration

The flow-state-monitor integrates with IBKR Borrow Sensor to fetch borrow rate data from snapshot files. The IBKR Borrow Sensor is a separate tool that collects and exports borrow rate data from Interactive Brokers to JSON files.

**Repository**: https://github.com/hoppefamily/ibkr-borrow-sensor

### Setup

1. **Install and run IBKR Borrow Sensor** (in a separate project):
   ```bash
   cd /path/to/ibkr-borrow-sensor
   npm install
   npm run demo  # Or set up scheduled collection
   ```

2. **Snapshot files are created** in `./output/` directory:
   - `borrow-state-AAPL-latest.json`
   - `borrow-state-TSLA-latest.json`
   - etc.

3. **Point flow-state-monitor to the snapshot directory**:
   ```bash
   export IBKR_SNAPSHOT_DIR=/path/to/ibkr-borrow-sensor/output
   ```

### Snapshot File Format

```json
{
  "symbol": "AAPL",
  "availability": 150000,
  "rate": "MEDIUM",
  "changeDirection": "up",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Rate buckets are mapped to percentages:
- `VERY_LOW` → 0.5%
- `LOW` → 2%
- `MEDIUM` → 5%
- `HIGH` → 10%
- `VERY_HIGH` → 25%
- `EXTREME` → 50%

### Python API

```python
from flow_state_monitor import FlowStateMonitor
from flow_state_monitor.alpaca_data import fetch_combined_data

# Fetch BOTH borrow rates (IBKR Borrow Sensor) and prices (Alpaca) - complete solution!
data = fetch_combined_data(
    symbol='AAPL',
    days=30,
    ibkr_snapshot_dir='./output',  # Path to IBKR Borrow Sensor snapshots
    alpaca_api_key='YOUR_KEY',
    alpaca_secret_key='YOUR_SECRET',
    paper=True
)

# Analyze
monitor = FlowStateMonitor()
results = monitor.analyze(**data)
print(results['summary'])
```

### Or Fetch Only Borrow Rates

```python
from flow_state_monitor.ibkr_borrow_data import fetch_ibkr_borrow_rates

# Fetch borrow rates from IBKR Borrow Sensor snapshots
borrow_data = fetch_ibkr_borrow_rates('AAPL', days=30, snapshot_dir='./output')

# Combine with your price data
monitor = FlowStateMonitor()
results = monitor.analyze(
    borrow_rates=borrow_data['borrow_rates'],
    prices=your_prices
)
```

### Command Line

```bash
# Default mode: IBKR Borrow Sensor + Alpaca (uses env vars)
flow-state-monitor AAPL --days 30

# Specify custom snapshot directory
flow-state-monitor AAPL --ibkr-snapshot-dir /path/to/snapshots

# IBKR Borrow Sensor + CSV prices
flow-state-monitor AAPL --price-csv prices.csv --ibkr-snapshot-dir ./output

# IBKR Borrow Sensor + IBKR prices
flow-state-monitor AAPL --use-ibkr --ibkr-snapshot-dir ./output
```

**Note**: Since IBKR Borrow Sensor provides point-in-time snapshots (not historical data), flow-state-monitor repeats the current rate for the requested number of days. For historical analysis, you'll need to maintain your own time-series database.

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
