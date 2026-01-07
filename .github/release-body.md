# flow-state-monitor v0.1.0

## 🎉 Initial Release

This is the first official release of flow-state-monitor as a private GitHub package!

### ✨ New Features

- **GitHub Packages Support**: Install via `pip install` with `--extra-index-url`
- **Git URL Installation**: Alternative simpler installation method
- **Automated Publishing**: GitHub Actions workflows for building, testing, and publishing
- **Comprehensive Documentation**: Complete installation and authentication guides
- **Relative Strength Analysis**: Compare stocks against SPY and QQQ benchmarks
- **Alpaca Integration**: Fetch price data from Alpaca Markets
- **Ortex Integration**: Fetch borrow rate data from Ortex API
- **CLI Tool**: Command-line interface for flow state monitoring

### 📦 Installation

**Method 1: GitHub Packages**
```bash
pip install flow-state-monitor --extra-index-url https://USERNAME:${GITHUB_TOKEN}@pip.pkg.github.com/hoppefamily/
```

**Method 2: Git URL**
```bash
pip install git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0
```

### 📚 Documentation

- [PACKAGE_INSTALLATION.md](PACKAGE_INSTALLATION.md) - Installation guide
- [GITHUB_PACKAGES_AUTH.md](GITHUB_PACKAGES_AUTH.md) - Authentication setup
- [PRIVATE_PACKAGE_SETUP.md](PRIVATE_PACKAGE_SETUP.md) - Package overview
- [README.md](README.md) - Main documentation

### 🔧 Requirements

- Python 3.8+
- PyYAML 6.0+
- Optional: alpaca-py, ib_insync

### ⚠️ Breaking Changes

None - this is the initial release.

### 🐛 Bug Fixes

None - this is the initial release.

### 📝 Notes

This is a private package designed for use within the hoppefamily ecosystem. It is not published to public PyPI.
