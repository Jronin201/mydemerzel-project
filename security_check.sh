# Security Check Script
# Run this before committing to ensure no secrets are accidentally included

echo "🔍 Checking for potential security issues..."

# Check if .env is properly ignored
if git check-ignore .env >/dev/null 2>&1; then
    echo "✅ .env file is properly ignored"
else
    echo "❌ WARNING: .env file is NOT ignored! Add it to .gitignore immediately!"
    exit 1
fi

# Check for any real API keys or secrets in tracked files (excluding legitimate code and docs)
if git ls-files | xargs grep -l -E "(sk-[a-zA-Z0-9]{48}|sk-proj-[a-zA-Z0-9_-]{100,}|AKIA[0-9A-Z]{16})" 2>/dev/null; then
    echo "❌ WARNING: Real API keys found in tracked files!"
    echo "Please review the files above and remove any sensitive information."
    exit 1
else
    echo "✅ No real API keys found in tracked files"
fi

# Check if .env contains placeholder values
if [ -f .env ]; then
    if grep -q "your-.*-here" .env; then
        echo "ℹ️  .env file contains placeholder values - remember to update with real values"
    else
        echo "✅ .env file appears to have real values"
    fi
else
    echo "ℹ️  No .env file found - you'll need to create one"
fi

echo "🛡️ Security check complete!"
