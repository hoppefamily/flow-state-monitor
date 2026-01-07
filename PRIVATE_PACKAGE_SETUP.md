# flow-state-monitor - Private Package Setup

This repository is consumed as a **private git dependency** that can be installed by other projects like `market-flow-dashboard`.

## Quick Setup Summary

### ✅ What's Been Configured

1. **Package Metadata** - `pyproject.toml` configured for GitHub installation
2. **GitHub Actions** - Automated workflows for building, testing, and publishing
3. **Installation Guide** - `PACKAGE_INSTALLATION.md` with comprehensive instructions
4. **Consumer Setup** - `market-flow-dashboard` configured to install this package

### 🚀 How to Use This Package

#### As a Consumer (in other projects)

In your `requirements.txt`:
```
flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0
```

Then install with:
```bash
pip install -r requirements.txt
```

#### As a Maintainer (publishing updates)

1. Update version in `pyproject.toml`
2. Commit changes
3. Create a git tag: `git tag v0.1.1 && git push origin v0.1.1`
4. Create a GitHub release (triggers automated publishing)

## Key Files

- **[PACKAGE_INSTALLATION.md](PACKAGE_INSTALLATION.md)** - Complete installation and usage guide
- **[GITHUB_PACKAGES_AUTH.md](GITHUB_PACKAGES_AUTH.md)** - Git authentication setup for private installs
- **[pyproject.toml](pyproject.toml)** - Package configuration and metadata
- **[.github/workflows/build-test.yml](.github/workflows/build-test.yml)** - Automated testing

## Installation Method

### Git (Recommended)

Install by pinning to a tag:

```bash
pip install "flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0"
```

📖 **See [GITHUB_PACKAGES_AUTH.md](GITHUB_PACKAGES_AUTH.md) for authentication setup.**

## Version Management

Current version: **0.1.0**

To update the version:
1. Edit `pyproject.toml`: `version = "0.1.1"`
2. Commit: `git commit -am "Bump version to 0.1.1"`
3. Tag: `git tag v0.1.1`
4. Push: `git push origin main --tags`
5. Create GitHub release

## GitHub Actions Workflows

### Build and Test (Automatic)
- Runs on: Push to main, PRs
- Tests: Python 3.8, 3.9, 3.10, 3.11, 3.12
- Status: Check `.github/workflows/build-test.yml`

### Publish Package (On Release)
- Runs on: New GitHub release
- Action: (Optional) create a tag/release for consumers to pin to

## Consumer Projects

Currently consumed by:
- **market-flow-dashboard** - Dashboard for monitoring market flow states

## Security & Access

- This is a **private repository**
- Access requires GitHub authentication
- Use Personal Access Token with `repo` scope for automated installations
- Never commit tokens to version control

## Development Workflow

1. **Make changes** in feature branches
2. **Run tests** locally: `pytest tests/`
3. **Create PR** to main branch
4. **CI runs** automatically (build-test.yml)
5. **Merge to main** after approval
6. **Create release** for new versions
7. **Package published** automatically

## Troubleshooting

### Cannot Install Package
- Check GitHub access: Do you have repo access?
- Verify authentication: Is `GITHUB_TOKEN` set?
- Check Python version: Must be 3.8+

### Import Errors After Installation
- Verify: `pip show flow-state-monitor`
- Check virtual environment is activated
- Reinstall: `pip uninstall flow-state-monitor && pip install ...`

### GitHub Actions Failing
- Check workflow logs in GitHub Actions tab
- Verify secrets are configured (if needed)
- Ensure tests pass locally first

## Support

For questions or issues:
1. Check [PACKAGE_INSTALLATION.md](PACKAGE_INSTALLATION.md) for detailed guide
2. Check GitHub Issues for known problems
3. Review GitHub Actions logs for CI/CD issues

## Best Practices

✅ **DO:**
- Pin versions in production: `@v0.1.0`
- Use virtual environments
- Keep tokens secure
- Test before releasing
- Document breaking changes

❌ **DON'T:**
- Commit API tokens
- Use `@main` in production
- Skip version tags
- Break semantic versioning

---

**Note**: This package is designed to be consumed by other projects in the hoppefamily ecosystem. It remains private and is not published to public PyPI.
