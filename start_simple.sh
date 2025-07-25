#!/bin/bash

# Simple memory-optimized startup for Render deployment
# This version uses inline gunicorn configuration to avoid dependency issues

echo "🚀 Starting Demerzel TTRPG Chatbot (Simple Configuration)..."

# Set memory-related environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

echo "📊 Memory optimization settings:"
echo "   - Single worker mode: ACTIVE"
echo "   - Lazy embedding loading: ACTIVE"
echo "   - Sync worker class: RELIABLE"

# Start with simple inline configuration
exec gunicorn app:app \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --worker-class sync \
    --max-requests 100 \
    --max-requests-jitter 20 \
    --timeout 120 \
    --preload-app \
    --log-level info \
    --access-logfile - \
    --error-logfile -
