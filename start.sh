#!/bin/bash
# start.sh - Quick development startup script

echo "🎮 Starting TTRPG Chatbot in development mode..."

# Quick environment check
if [ ! -f .env ]; then
    echo "⚠️  No .env file found - using defaults"
    echo "ℹ️  Create .env from .env.example for production"
fi

# Start Flask development server
echo "🔧 Starting development server on http://localhost:5000"
echo "📱 Your TTRPG chatbot will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop"

export FLASK_ENV=development
export FLASK_DEBUG=1
python3 app.py
