#!/bin/bash

# Memory-optimized startup script for Render deployment
# This script monitors memory usage and provides warnings

echo "🚀 Starting Demerzel TTRPG Chatbot with memory optimization..."

# Set memory-related environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export MALLOC_TRIM_THRESHOLD_=100000

# Optional: Set specific TTRPG system to preload (reduces cold start time)
# Uncomment one of these lines to preload a specific system:
# export PRELOAD_TTRPG_SYSTEM="dune"
# export PRELOAD_TTRPG_SYSTEM="the-one-ring"
# export PRELOAD_TTRPG_SYSTEM="mouse-guard"

echo "📊 Memory optimization settings:"
echo "   - Single worker mode: ACTIVE"
echo "   - Lazy embedding loading: ACTIVE"
echo "   - Automatic cache eviction: ACTIVE"
echo "   - Garbage collection: AGGRESSIVE"

# Check available memory
if command -v free &> /dev/null; then
    echo "💾 Available memory:"
    free -h
elif command -v vm_stat &> /dev/null; then
    echo "💾 Memory info (macOS):"
    vm_stat
else
    echo "💾 Memory monitoring tools not available"
fi

# Check embedding files
echo "📁 Checking embedding files..."
if [ -d "embeddings" ]; then
    echo "   Embedding directory found:"
    ls -lh embeddings/*.json 2>/dev/null | while read line; do
        echo "   $line"
    done
    
    total_size=$(du -sh embeddings/ 2>/dev/null | cut -f1)
    echo "   Total embedding size: $total_size"
    
    if [ -n "$total_size" ]; then
        # Extract numeric value (assuming format like "170M" or "1.2G")
        size_num=$(echo "$total_size" | sed 's/[^0-9.]//g')
        size_unit=$(echo "$total_size" | sed 's/[0-9.]//g')
        
        case $size_unit in
            "M"|"MB")
                if (( $(echo "$size_num > 200" | bc -l 2>/dev/null || echo 0) )); then
                    echo "   ⚠️  WARNING: Large embedding files detected!"
                    echo "   Memory optimization is CRITICAL for this deployment"
                fi
                ;;
            "G"|"GB")
                echo "   ⚠️  WARNING: Very large embedding files detected!"
                echo "   Memory optimization is ESSENTIAL for this deployment"
                ;;
        esac
    fi
else
    echo "   ⚠️  Embedding directory not found - creating..."
    mkdir -p embeddings
fi

# Start the application with memory-optimized gunicorn
echo "🔄 Starting application with memory-optimized configuration..."

# Use the memory-optimized requirements
if [ -f "requirements-prod.txt" ]; then
    echo "📦 Using production requirements (memory-optimized)"
    export REQUIREMENTS_FILE="requirements-prod.txt"
else
    echo "📦 Using standard requirements"
    export REQUIREMENTS_FILE="requirements.txt"
fi

# Start gunicorn with the optimized configuration
if [ -f "gunicorn.conf.py" ]; then
    echo "   Using custom Gunicorn configuration for memory optimization"
    exec gunicorn --config gunicorn.conf.py app:app
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
