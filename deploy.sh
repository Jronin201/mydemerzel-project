#!/bin/bash
# deploy.sh - Simple deployment script for personal use

echo "🚀 Starting personal TTRPG chatbot deployment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one from .env.example"
    echo "ℹ️  Copy .env.example to .env and fill in your API keys"
    exit 1
fi

# Verify Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8 or higher"
    exit 1
fi

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements-prod.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check if we're in development mode
if [ "$1" = "--dev" ]; then
    echo "🔧 Starting development server..."
    python3 app.py
else
    # Start with gunicorn for production
    echo "🌟 Starting production server on http://0.0.0.0:5000"
    echo "📱 Access your TTRPG chatbot at: http://localhost:5000"
    echo "🛑 Press Ctrl+C to stop the server"
    gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
fi
