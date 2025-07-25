# Git Configuration Setup Guide

This guide helps prevent Git GPG signing errors and ensures smooth development workflow.

## For Development Environments

### 1. Disable GPG Signing (Recommended for Development)

```bash
# Disable GPG signing globally
git config --global commit.gpgsign false

# Set your user information
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. Alternative: Set up GPG Properly (Advanced)

If you need GPG signing, follow these steps:

```bash
# Generate a new GPG key
gpg --gen-key

# List GPG keys to get the key ID
gpg --list-secret-keys --keyid-format LONG

# Set the GPG key in Git (replace KEY_ID with your actual key ID)
git config --global user.signingkey KEY_ID

# Ensure GPG is properly configured
git config --global gpg.program gpg
```

## For Production/Deployment Environments

### Environment Variables

Set `DEPLOYMENT_ENV=render` (or your deployment platform) to enable deployment-specific Git configuration.

### Required Environment Variables

```bash
# For local development
FLASK_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key

# For deployment (optional)
DEPLOYMENT_ENV=render
GITHUB_TOKEN=your-github-token (for automated deployments)
```

## Troubleshooting Common Git Issues

### Error: "gpg failed to sign the data"

**Solution 1: Disable GPG signing**

```bash
git config --global commit.gpgsign false
```

**Solution 2: Fix GPG setup**

```bash
# Check if GPG is working
echo "test" | gpg --clearsign

# If it fails, you may need to restart gpg-agent
gpgconf --kill gpg-agent
gpgconf --launch gpg-agent
```

### Error: "Author identity unknown"

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Error: "remote origin already exists"

This is usually harmless and occurs during deployment setup. The application handles this gracefully.

## Best Practices

1. **Development**: Disable GPG signing for faster commits
2. **Production**: Use environment variables for sensitive configuration
3. **Team**: Document Git configuration requirements in README
4. **Security**: Never commit sensitive tokens or keys

## Quick Fix Commands

```bash
# Reset Git configuration if things go wrong
git config --global --unset commit.gpgsign
git config --global --unset user.signingkey
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Test that Git is working
git status
git add .
git commit -m "Test commit"
```
