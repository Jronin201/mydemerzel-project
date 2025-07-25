#!/bin/bash
# scripts/lockdown_deploy.sh
# Deployment script for locked-down/restricted environments

set -e

echo "🔒 Deploying Demerzel Project for Locked-Down Environment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "----------------------------"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $($PYTHON_CMD --version)"

# Check pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "❌ pip not found. Please install pip first."
    exit 1
fi

echo "✅ pip found"

# Check internet connectivity for initial setup
if curl -s --head "https://api.openai.com" > /dev/null 2>&1; then
    echo "✅ Internet access available"
    INTERNET_AVAILABLE=true
else
    echo "⚠️  Internet access limited - will work in offline mode"
    INTERNET_AVAILABLE=false
fi

echo ""
echo "🔧 Installing Dependencies..."
echo "----------------------------"

# Install Python dependencies
$PYTHON_CMD -m pip install -r requirements.txt --user

echo ""
echo "📁 Setting up Embedding Files..."
echo "--------------------------------"

# Check if embedding files exist
EMBEDDINGS_EXIST=false
if [ -f "embeddings/dune_optimized.json" ] && \
   [ -f "embeddings/the-one-ring_optimized.json" ] && \
   [ -f "embeddings/mouse-guard_optimized.json" ]; then
    echo "✅ All embedding files already present"
    EMBEDDINGS_EXIST=true
fi

# Try to download embeddings if not present and internet is available
if [ "$EMBEDDINGS_EXIST" = false ] && [ "$INTERNET_AVAILABLE" = true ]; then
    echo "📥 Attempting to download embeddings from Supabase..."
    if [ -f "./scripts/download_embeddings.sh" ]; then
        chmod +x ./scripts/download_embeddings.sh
        if ./scripts/download_embeddings.sh; then
            echo "✅ Embeddings downloaded successfully"
            EMBEDDINGS_EXIST=true
        else
            echo "⚠️  Embedding download failed"
        fi
    fi
fi

echo ""
echo "🔑 Environment Configuration..."
echo "------------------------------"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Supabase Configuration (for embedding downloads)
SUPABASE_PROJECT_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_BUCKET_NAME=ttrpg-embeddings

# Optional: Deployment Environment
DEPLOYMENT_ENV=lockdown
EOF
    echo "📝 Created .env template. Please edit with your API keys."
else
    echo "✅ .env file found"
fi

echo ""
echo "🚀 Deployment Summary:"
echo "======================"

if [ "$EMBEDDINGS_EXIST" = true ]; then
    echo "✅ Embedding files: Ready"
else
    echo "⚠️  Embedding files: Missing - limited functionality"
    echo "   💡 To get embeddings:"
    echo "   1. On a computer with internet: run './scripts/download_embeddings.sh'"
    echo "   2. Copy the embeddings/ folder to this deployment"
    echo "   3. Or manually download from Supabase dashboard"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run: $PYTHON_CMD app.py"
echo "3. Access at: http://localhost:5000"

echo ""
echo "🔧 Manual Embedding Setup (if needed):"
echo "======================================="
echo "If embeddings are missing, download these files to the embeddings/ folder:"
echo "- dune_optimized.json"
echo "- the-one-ring_optimized.json" 
echo "- mouse-guard_optimized.json"
echo ""
echo "You can get them from:"
echo "1. Another deployment with internet access"
echo "2. Supabase dashboard (if configured)"
echo "3. Generate locally with: ./run_embedding_optimization.sh"

echo ""
echo "✅ Lockdown deployment preparation complete!"
