# 🔒 Locked-Down Computer Deployment Guide

## Overview

This guide explains how to deploy the Demerzel TTRPG Chatbot on **locked-down, online-only computers** where you may have restricted access to package managers, limited internet access, or security restrictions.

## 🎯 What Works in Locked-Down Environments

### ✅ **Fully Functional Features:**

- Chat interface and conversation history
- Character information tracking
- User session management
- All TTRPG system interfaces (Dune, The One Ring, Mouse Guard)
- Local file operations and data persistence

### ⚠️ **Limited Features (requires internet):**

- AI chat responses (requires OpenAI API access)
- Embedding file downloads (one-time setup)

### ❌ **Not Required:**

- Package compilation or build tools
- Admin/root access for dependencies
- Complex system configurations

## 🚀 Quick Deployment

### Option 1: Automated Setup (Recommended)

```bash
# Clone the project
git clone https://github.com/Jronin201/mydemerzel-project.git
cd mydemerzel-project

# Run the lockdown deployment script
./scripts/lockdown_deploy.sh
```

### Option 2: Manual Setup

```bash
# Install Python dependencies
python -m pip install -r requirements.txt --user

# Download embeddings (if internet available)
./scripts/download_embeddings.sh

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Start the application
python app.py
```

## 📁 Embedding Files for Offline Setup

If the computer has no internet access, you'll need to transfer these files manually:

```
embeddings/
├── dune_optimized.json          (~111MB)
├── the-one-ring_optimized.json  (~6.5MB)
└── mouse-guard_optimized.json   (~53MB)
```

### How to Get Embedding Files:

1. **From another deployment:**

   ```bash
   # On computer with internet
   git clone https://github.com/Jronin201/mydemerzel-project.git
   cd mydemerzel-project
   ./scripts/download_embeddings.sh

   # Transfer the entire embeddings/ folder to target computer
   ```

2. **From Supabase dashboard:**

   - Login to your Supabase project
   - Go to Storage → ttrpg-embeddings bucket
   - Download the 3 files manually
   - Place in `embeddings/` folder

3. **Generate locally:**
   ```bash
   # If you have the source PDFs and OpenAI access
   ./run_embedding_optimization.sh
   ```

## 🔧 Environment Configuration

### Minimal .env file:

```bash
# Required for AI responses
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Supabase (for embedding downloads)
SUPABASE_PROJECT_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_BUCKET_NAME=ttrpg-embeddings
```

### For completely offline mode:

```bash
# Still needs OpenAI API for chat, but embeddings are local
OPENAI_API_KEY=your-openai-api-key-here
DEPLOYMENT_ENV=offline
```

## 🚨 Troubleshooting Common Issues

### "No module named 'xyz'" Error

```bash
# Install dependencies with user flag
python -m pip install -r requirements.txt --user

# Or install specific package
python -m pip install flask --user
```

### "Permission denied" Error

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Or run with bash explicitly
bash scripts/download_embeddings.sh
```

### "Embedding files not found" Warning

- The app will still work but with limited TTRPG knowledge
- Transfer embedding files manually (see above)
- Or run with internet access once to download

### API Rate Limits

```bash
# Add to .env to reduce API usage
OPENAI_MODEL=gpt-3.5-turbo  # Instead of gpt-4o
MAX_TOKENS=500              # Limit response length
```

## 📊 Deployment Verification

### Check embedding status:

```bash
python -c "
from lockdown_embedding_loader import get_embedding_status
import json
status = get_embedding_status()
print(json.dumps(status, indent=2))
"
```

### Test basic functionality:

```bash
# Start app
python app.py

# Visit http://localhost:5000
# Try logging in with any username/password
# Test each TTRPG system interface
```

## 🎯 Deployment Scenarios

### Scenario 1: Corporate Network (Internet Access)

- ✅ Use automated setup script
- ✅ Download embeddings automatically
- ✅ Full functionality

### Scenario 2: Air-Gapped System (No Internet)

- ⚠️ Transfer embedding files manually
- ⚠️ Install dependencies on connected system first
- ✅ Local functionality works perfectly

### Scenario 3: Limited Internet (API only)

- ✅ Use existing embeddings
- ✅ OpenAI API for chat responses
- ✅ Full functionality with pre-installed embeddings

## 💾 File Size Requirements

```
Total project size: ~25MB (without embeddings)
With embeddings: ~200MB total
Python dependencies: ~100MB
```

## 🔄 Updates and Maintenance

### Update code only (preserves embeddings):

```bash
git pull origin main
# Embeddings remain unchanged
```

### Update embeddings:

```bash
./scripts/download_embeddings.sh
# Or replace files manually
```

### Backup important data:

```bash
# Chat histories and character data
tar -czf backup.tar.gz chat_histories/ character_info/ *.json
```

## 📞 Support for Locked-Down Deployments

If you encounter issues specific to locked-down environments:

1. Check the deployment verification steps above
2. Review the troubleshooting section
3. Use the `lockdown_deployment.sh` script for automated diagnosis
4. File an issue with your deployment environment details

The system is designed to be as self-contained and offline-friendly as possible while maintaining full functionality.
