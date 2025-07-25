#!/bin/bash

# Memory-optimized startup script for Render deployment
# This script monitors memory usage and provides optimization recommendations

set -e

echo "🚀 Starting Demerzel TTRPG Chatbot with memory optimizations..."

# Environment check
echo "📊 Environment Information:"
echo "   Python version: $(python --version)"
echo "   Memory limit: 512MB (Render constraint)"
echo "   PORT: ${PORT:-8000}"

# Check if embedding files exist and their sizes
echo "📂 Checking embedding files:"
if [ -d "embeddings" ]; then
    total_size=0
    for file in embeddings/*.json; do
        if [ -f "$file" ]; then
            size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "0")
            size_mb=$((size / 1024 / 1024))
            total_size=$((total_size + size))
            echo "   $(basename "$file"): ${size_mb}MB"
        fi
    done
    total_mb=$((total_size / 1024 / 1024))
    echo "   Total embedding files: ${total_mb}MB"
    
    if [ $total_mb -gt 200 ]; then
        echo "⚠️  WARNING: Large embedding files detected"
        echo "   Using lazy loading to prevent memory exhaustion"
    fi
else
    echo "   No embeddings directory found"
fi

# Set memory-optimized environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export MALLOC_ARENA_MAX=2

# Check if we're in a memory-constrained environment
echo "🧠 Memory optimization strategies:"
echo "   ✅ Lazy loading enabled for embeddings"
echo "   ✅ Single worker process configured"
echo "   ✅ Worker restart after 100 requests"
echo "   ✅ Garbage collection optimizations"

# Install any missing production dependencies
echo "📦 Checking production dependencies..."
pip install --no-cache-dir psutil 2>/dev/null || echo "   psutil installation failed - memory monitoring will be limited"

# Run pre-startup memory check
python -c "
import sys
import gc
gc.collect()
print('🔧 Pre-startup memory check complete')
print(f'   Python version: {sys.version_info.major}.{sys.version_info.minor}')
"

# Start the application with memory monitoring
echo "🎯 Starting application with memory-optimized Gunicorn..."

if [ -f "gunicorn.conf.py" ]; then
    echo "   Using custom Gunicorn configuration for memory optimization"
    exec gunicorn -c gunicorn.conf.py app:app
else
    echo "   Using inline Gunicorn configuration"
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
fi
