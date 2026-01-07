# Installing flow-state-monitor as a Private Package

This document explains how to install and use flow-state-monitor as a private package from GitHub.

## For Consumers (e.g., market-flow-dashboard)

### Method 1: Install from GitHub Packages (Recommended)

Install like a regular PyPI package using `--extra-index-url`:

```bash
# Install latest version
pip install flow-state-monitor --extra-index-url https://USERNAME:${GITHUB_TOKEN}@maven.pkg.github.com/hoppefamily/

# Install specific version
pip install flow-state-monitor==0.1.0 --extra-index-url https://USERNAME:${GITHUB_TOKEN}@maven.pkg.github.com/hoppefamily/

# With optional dependencies
pip install flow-state-monitor[alpaca] --extra-index-url https://USERNAME:${GITHUB_TOKEN}@maven.pkg.github.com/hoppefamily/
```

**Setup required**: See [GITHUB_PACKAGES_AUTH.md](GITHUB_PACKAGES_AUTH.md) for authentication setup.

### Method 2: Install from Git Repository (Simpler Authentication)

Since this is a private repository, the easiest way to install it is directly from GitHub:

```bash
# Install from main branch
pip install git+https://github.com/hoppefamily/flow-state-monitor.git@main

# Install from a specific version tag
pip install git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0

# Install from a specific branch
pip install git+https://github.com/hoppefamily/flow-state-monitor.git@feature/relative-strength-analysis
```

### Method 2: Install with GitHub Token (For CI/CD)

For automated deployments or CI/CD pipelines, use a GitHub Personal Access Token:

```bash
# Set token as environment variable
export GITHUB_TOKEN=your_personal_access_token

# Install with authentication
pip install git+https://${GITHUB_TOKEN}@github.com/hoppefamily/flow-state-monitor.git@main
```

### In requirements.txt

**Method 1: GitHub Packages (cleaner, version pinning)**

```
# requirements.txt
flow-state-monitor==0.1.0
```

Then install with:
```bash
pip install -r requirements.txt --extra-index-url https://USERNAME:${GITHUB_TOKEN}@maven.pkg.github.com/hoppefamily/
```

**Method 2: Git URL (simpler auth)**

```
# flow-state-monitor from GitHub
git+https://github.com/hoppefamily/flow-state-monitor.git@main

# Or pinned version
git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0
```

### With Optional Dependencies

If you need IBKR or Alpaca support:

```bash
# Install with Alpaca support
pip install "flow-state-monitor[alpaca] @ git+https://github.com/hoppefamily/flow-state-monitor.git@main"

# Install with IBKR support
pip install "flow-state-monitor[ibkr] @ git+https://github.com/hoppefamily/flow-state-monitor.git@main"

# Install with dev dependencies
pip install "flow-state-monitor[dev] @ git+https://github.com/hoppefamily/flow-state-monitor.git@main"
```

In `requirements.txt`:

```
flow-state-monitor[alpaca] @ git+https://github.com/hoppefamily/flow-state-monitor.git@main
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
    pip install git+https://${{ secrets.GITHUB_TOKEN }}@github.com/hoppefamily/flow-state-monitor.git@main
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
