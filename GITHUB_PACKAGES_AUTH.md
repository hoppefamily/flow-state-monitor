# GitHub Packages Authentication Setup

To install packages from GitHub Packages, you need to authenticate with a Personal Access Token.

## Creating a Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "Package Installation"
4. Select scopes:
   - `read:packages` - Download packages
   - `repo` - Access private repositories (if needed)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

## Configure pip for GitHub Packages

Create or edit `~/.netrc` file:

```bash
cat >> ~/.netrc << EOF
machine pip.pkg.github.com
login YOUR_GITHUB_USERNAME
password YOUR_PERSONAL_ACCESS_TOKEN
EOF

# Secure the file
chmod 600 ~/.netrc
```

Or create `~/.pip/pip.conf`:

```bash
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
extra-index-url = https://YOUR_GITHUB_USERNAME:YOUR_PERSONAL_ACCESS_TOKEN@pip.pkg.github.com/hoppefamily/
EOF
```

## Environment Variable Method (Recommended for CI/CD)

```bash
# Set environment variable
export PIP_EXTRA_INDEX_URL=https://YOUR_GITHUB_USERNAME:${GITHUB_TOKEN}@pip.pkg.github.com/hoppefamily/

# Now pip install will work
pip install flow-state-monitor
```

## Installing the Package

Once authenticated, install normally:

```bash
# Method 1: Using extra-index-url flag
pip install flow-state-monitor --extra-index-url https://YOUR_USERNAME:${GITHUB_TOKEN}@pip.pkg.github.com/hoppefamily/

# Method 2: After configuring pip.conf (no flags needed)
pip install flow-state-monitor

# Method 3: Using netrc (no flags needed)
pip install flow-state-monitor
```

## In requirements.txt

```
# requirements.txt
flow-state-monitor==0.1.0
```

Then install with:

```bash
pip install -r requirements.txt --extra-index-url https://USERNAME:${GITHUB_TOKEN}@pip.pkg.github.com/hoppefamily/
```

## For GitHub Actions

```yaml
- name: Configure pip for GitHub Packages
  run: |
    echo "extra-index-url=https://${{ secrets.GITHUB_TOKEN }}@pip.pkg.github.com/hoppefamily/" >> $HOME/.pip/pip.conf

- name: Install dependencies
  run: |
    pip install -r requirements.txt
```

## Security Notes

⚠️ **Never commit tokens to version control!**
- Use environment variables
- Add `.netrc` and `pip.conf` to `.gitignore`
- Use GitHub Actions secrets for CI/CD
- Rotate tokens regularly

## Alternative: Git URL Method

If GitHub Packages authentication is problematic, you can still use:

```bash
pip install git+https://github.com/hoppefamily/flow-state-monitor.git@main
```

This uses SSH/HTTPS git authentication instead of package registry authentication.
