# Installing flow-state-monitor as a Private Package

This document explains how to install and use flow-state-monitor as a private package from GitHub.

## For Consumers (e.g., market-flow-dashboard)

### Install from Git (Recommended)

Install directly from the GitHub repo (pin to a tag for reproducibility):

```bash
# Recommended: install a tagged version
pip install "flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0"

# Development only: track main
pip install "flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@main"
```

**Auth required (private repo):** See [GITHUB_PACKAGES_AUTH.md](GITHUB_PACKAGES_AUTH.md) for recommended authentication patterns for local dev and CI.

### In requirements.txt

```
# requirements.txt
flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0
```

Then install with:
```bash
pip install -r requirements.txt
```

### With Optional Dependencies

If you need IBKR or Alpaca support:

```bash
# Install with Alpaca support
pip install "flow-state-monitor[alpaca] @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0"

# Install with IBKR support
pip install "flow-state-monitor[ibkr] @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0"

# Install with dev dependencies
pip install "flow-state-monitor[dev] @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0"
```

In `requirements.txt`:

```
flow-state-monitor[alpaca] @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0
```

## For Package Maintainers

### Creating a New Release

1. Update the version in `pyproject.toml`:
   ```toml
   version = "0.1.1"
   ```

2. Commit and push changes:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.1.1"
   git push origin main
   ```

3. Create a new release on GitHub:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

4. Go to GitHub → Releases → Create a new release
   - Tag: `v0.1.1`
   - Title: `v0.1.1`
   - Description: List changes and features
   - Click "Publish release"

5. The GitHub Actions workflow will automatically build and publish the package

   **Note**: This repo is currently consumed via git tags (VCS installs). There is no GitHub Packages publish step.

### Manual Package Building

To build the package locally:

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# - dist/flow_state_monitor-0.1.0-py3-none-any.whl
# - dist/flow-state-monitor-0.1.0.tar.gz
```

### Testing the Package

Before publishing, test that the package works:

```bash
# Build the package
python -m build

# Install locally
pip install dist/flow_state_monitor-0.1.0-py3-none-any.whl

# Test it
flow-state-monitor --help
```

## Authentication Setup

### GitHub Personal Access Token

For consuming this package in other projects or CI/CD:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope (for private repositories)
3. Save token securely (it won't be shown again)
4. Use in pip install commands or CI/CD secrets

### In GitHub Actions

Add to your workflow:

```yaml
- name: Install private packages
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
      pip install "flow-state-monitor @ git+https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/hoppefamily/flow-state-monitor.git@v0.1.0"
```

The `GITHUB_TOKEN` is automatically available in GitHub Actions.

## Usage After Installation

Once installed, use it like any Python package:

```python
from flow_state_monitor import FlowStateMonitor

monitor = FlowStateMonitor()
results = monitor.analyze(borrow_rates, prices)
```

Or via CLI:

```bash
flow-state-monitor AAPL --days 30
```

## Troubleshooting

### Authentication Errors

If you get a 404 or authentication error:

1. Verify you have access to the repository
2. Check your GitHub token has `repo` scope
3. Ensure the token is correctly set in the environment

### Installation Failures

If pip install fails:

1. Check you're using Python 3.8 or later
2. Try upgrading pip: `pip install --upgrade pip`
3. Check network connectivity to GitHub

### Import Errors

If you get import errors after installation:

1. Verify installation: `pip show flow-state-monitor`
2. Check you're in the correct virtual environment
3. Reinstall: `pip uninstall flow-state-monitor && pip install git+https://...`

## Best Practices

1. **Pin versions in production**: Use specific tags instead of `@main`
2. **Use virtual environments**: Always install in a venv
3. **Test before deploying**: Run tests after installing the package
4. **Keep tokens secure**: Never commit tokens to version control
5. **Regular updates**: Keep dependencies and package versions current

## See Also

- [Python Packaging User Guide](https://packaging.python.org/)
- [GitHub: Working with private packages](https://docs.github.com/en/packages/working-with-a-github-packages-registry)
- [pip: VCS Support](https://pip.pypa.io/en/stable/topics/vcs-support/)
