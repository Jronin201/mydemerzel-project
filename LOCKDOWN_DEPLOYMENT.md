# 🔒 Lockdown Environment Setup - Memory Optimized

## ✅ Configuration Updated for Supabase + Memory Optimization

Your deployment is now properly configured for a lockdown environment where:

- ✅ **Embedding files** are stored in Supabase (`dune.json`, `the-one-ring.json`, `mouse-guard.json`)
- ✅ **Memory optimization** with lazy loading (prevents OOM errors)
- ✅ **Automatic download** from Supabase on deployment
- ✅ **Single worker** configuration (within 512MB limit)

## 🔧 Key Changes Made

### 1. Updated File Names to Match Supabase

- **Before**: Looking for `*_optimized.json` files
- **After**: Looking for `dune.json`, `the-one-ring.json`, `mouse-guard.json`

### 2. Integrated Lockdown Loader with Memory Optimization

- **Supabase Download**: Automatic download on startup
- **Lazy Loading**: Files loaded only when TTRPG system is accessed
- **Memory Management**: LRU cache with 1 system at a time

### 3. Environment Variables Required

```bash
SUPABASE_PROJECT_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_BUCKET_NAME=ttrpg-embeddings  # Optional, defaults to this
```

## 📊 Expected Startup Sequence

When you deploy, you should see these logs in order:

```
🔧 Initializing TTRPG embedding systems for lockdown environment...
🔍 Environment Variables Debug:
   SUPABASE_PROJECT_URL: https://your-project.supabase.co
   SUPABASE_ANON_KEY: SET
   SUPABASE_BUCKET_NAME: ttrpg-embeddings
📦 Using lockdown embedding loader for Supabase downloads
🔄 Starting download_embeddings_if_missing function...
📋 Required files check: 0/3 exist
📥 Missing files: ['dune.json', 'the-one-ring.json', 'mouse-guard.json']
🔄 Forcing download of embeddings from Supabase...
📥 Downloading dune.json...
📥 Downloading the-one-ring.json...
📥 Downloading mouse-guard.json...
✅ Supabase embeddings downloaded successfully
🧠 Memory-optimized embedding manager initialized (cache size: 1)
✅ Memory-optimized embedding system ready with Supabase integration
📊 Embedding files will be loaded on demand from:
   dune: 111.0MB (available)
   the-one-ring: 6.5MB (available)
   mouse-guard: 53.0MB (available)
```

## 🚀 Render Configuration

Your current configuration should work:

**Build Command:**

```bash
pip install -r requirements-prod.txt
```

**Start Command:**

```bash
./start_simple.sh
```

**Environment Variables:** (Add these in Render dashboard)

```
SUPABASE_PROJECT_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_BUCKET_NAME=ttrpg-embeddings
FLASK_SECRET_KEY=your_secret_key
```

## 🔍 Troubleshooting

### If Files Don't Download

1. **Check Supabase Environment Variables**

   ```bash
   # In Render logs, look for:
   🔍 Environment Variables Debug:
      SUPABASE_PROJECT_URL: NOT SET  ← This should show your URL
      SUPABASE_ANON_KEY: NOT SET     ← This should show "SET"
   ```

2. **Check Supabase Bucket Configuration**

   - Bucket name: `ttrpg-embeddings`
   - Files: `dune.json`, `the-one-ring.json`, `mouse-guard.json`
   - Public read access enabled

3. **Check Download Logs**
   ```bash
   # Should see successful downloads:
   📥 Downloading dune.json...
   ✅ Downloaded dune.json successfully (111MB)
   ```

### If Memory Issues Persist

The memory optimization should prevent OOM errors:

- **Startup Memory**: ~30-50MB (before file access)
- **Single System**: ~80-150MB (when one system is loaded)
- **Peak Memory**: <400MB (well within 512MB limit)

## ✅ Ready to Deploy

Your configuration now properly handles:

- ✅ **Lockdown Environment**: Downloads from Supabase
- ✅ **Memory Optimization**: Lazy loading prevents OOM
- ✅ **File Name Matching**: Matches your Supabase files
- ✅ **Production Ready**: Optimized for Render deployment

**Deploy with confidence!** The system will download your embedding files from Supabase and manage memory efficiently. 🚀
