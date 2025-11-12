#!/bin/bash
# Script to generate optimized embeddings with proper environment setup

echo "🚀 GENERATING OPTIMIZED EMBEDDINGS"
echo "=================================="

# Load environment variables
if [ -f .env ]; then
    echo "📁 Loading environment variables from .env..."
    source .env
else
    echo "⚠️  No .env file found"
fi

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not found. Please set it in your .env file."
    exit 1
else
    echo "✅ OpenAI API key loaded: ${OPENAI_API_KEY:0:10}...${OPENAI_API_KEY: -4}"
fi

# Show current embeddings before optimization
echo ""
echo "📊 CURRENT EMBEDDINGS:"
if [ -f "embeddings/dune.json" ]; then
    size=$(du -h embeddings/dune.json | cut -f1)
    echo "   • dune.json: $size"
fi
if [ -f "embeddings/the-witcher.json" ]; then
    size=$(du -h embeddings/the-witcher.json | cut -f1)
    echo "   • the-witcher.json: $size"
fi

echo ""
echo "⏳ Starting optimization process..."
echo "   This will generate new embedding files with '_optimized' suffix"
echo "   The process may take 5-15 minutes depending on document size"
echo ""

# Run the optimization script
export OPENAI_API_KEY="$OPENAI_API_KEY"
/workspaces/mydemerzel-project/.venv/bin/python generate_optimized_embeddings.py

# Check if new files were created
echo ""
echo "📋 OPTIMIZATION RESULTS:"
if [ -f "embeddings/dune_optimized.json" ]; then
    size=$(du -h embeddings/dune_optimized.json | cut -f1)
    echo "   ✅ dune_optimized.json: $size"
fi
if [ -f "embeddings/the-witcher_optimized.json" ]; then
    size=$(du -h embeddings/the-witcher_optimized.json | cut -f1)
    echo "   ✅ the-witcher_optimized.json: $size"
fi

echo ""
echo "🎉 Optimization complete!"
echo "   Your Flask app will automatically use the optimized embeddings"
echo "   when you restart it (app.py checks for '_optimized' files first)"
