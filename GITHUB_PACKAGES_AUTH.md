# Git Authentication Setup (Private Repo)

flow-state-monitor is consumed via `pip` VCS installs (git URLs), not via a package registry.
This document explains how to authenticate to GitHub so `pip install "flow-state-monitor @ git+https://..."` works.

## Creating a Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "Package Installation"
4. Select scopes:
   - `read:packages` - Download packages
   - `repo` - Access private repositories (if needed)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

## Installing the Package

Recommended (pin to a tag):

```bash
pip install "flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0"
```

In `requirements.txt`:

```text
flow-state-monitor @ git+https://github.com/hoppefamily/flow-state-monitor.git@v0.1.0
```

## For GitHub Actions

```yaml
- name: Install flow-state-monitor (private repo)
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    pip install "flow-state-monitor @ git+https://x-access-token:${GITHUB_TOKEN}@github.com/hoppefamily/flow-state-monitor.git@v0.1.0"
```

## Security Notes

⚠️ **Never commit tokens to version control!**
- Use environment variables
- Add `.netrc` and `pip.conf` to `.gitignore`
- Use GitHub Actions secrets for CI/CD
- Rotate tokens regularly

## Alternative: Git URL Method

You can also install via SSH (common for developers with SSH keys configured):

```bash
pip install "flow-state-monitor @ git+ssh://git@github.com/hoppefamily/flow-state-monitor.git@v0.1.0"
```
