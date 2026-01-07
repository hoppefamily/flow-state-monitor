# Quick Reference: Managing the Private Package

## Publishing a New Version

```bash
# 1. Update version in pyproject.toml
vim pyproject.toml  # Change version = "0.1.1"

# 2. Commit changes
git add pyproject.toml
git commit -m "Bump version to 0.1.1"

# 3. Create and push tag
git tag v0.1.1
git push origin main --tags

# 4. Create GitHub Release
# Go to: https://github.com/hoppefamily/flow-state-monitor/releases/new
# - Tag: v0.1.1
# - Title: Release v0.1.1
# - Description: List changes
# - Click "Publish release"

# GitHub Actions will automatically build and test
```

## Installing in Other Projects

```bash
# In requirements.txt
flow-state-monitor==0.1.0

# Install with
pip install -r requirements.txt --extra-index-url https://USERNAME:${GITHUB_TOKEN}@maven.pkg.github.com/hoppefamily/
```

## Testing Before Release

```bash
# Run tests
pytest tests/ -v

# Build package
python -m build

# Install and test locally
pip install dist/*.whl
flow-state-monitor --help
```

## Updating in market-flow-dashboard

```bash
cd market-flow-dashboard
pip install --upgrade --force-reinstall git+https://github.com/hoppefamily/flow-state-monitor.git@main
```

## Common Commands

```bash
# Check current version
grep "version = " pyproject.toml

# List installed version
pip show flow-state-monitor

# Build package locally
python -m build

# View GitHub Actions status
open https://github.com/hoppefamily/flow-state-monitor/actions
```

## Version Numbering

Follow Semantic Versioning (SemVer):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backward compatible
- **PATCH** (0.1.1): Bug fixes, backward compatible

Examples:
- `0.1.0` → `0.1.1`: Bug fix
- `0.1.0` → `0.2.0`: New feature added
- `0.9.0` → `1.0.0`: First stable release

## Troubleshooting

### Build Fails
```bash
# Clean build artifacts
rm -rf dist/ build/ *.egg-info/

# Upgrade build tools
pip install --upgrade build setuptools wheel

# Try again
python -m build
```

### GitHub Actions Failing
1. Check logs: GitHub → Actions → Click failing workflow
2. Common issues:
   - Tests failing: Fix code, push again
   - Build errors: Check pyproject.toml syntax
   - Permission errors: Check workflow permissions

### Can't Install in Other Projects
```bash
# Check authentication
git ls-remote https://github.com/hoppefamily/flow-state-monitor.git

# If authentication needed
export GITHUB_TOKEN=your_token
pip install git+https://${GITHUB_TOKEN}@github.com/hoppefamily/flow-state-monitor.git@main
```

## Documentation Files

- **PRIVATE_PACKAGE_SETUP.md** - Overview and setup summary
- **PACKAGE_INSTALLATION.md** - Detailed installation guide
- **README.md** - Main documentation
- **.github/workflows/publish-package.yml** - Publishing workflow
- **.github/workflows/build-test.yml** - Testing workflow
