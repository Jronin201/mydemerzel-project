# Supabase Embedding Storage Setup

This guide shows how to use Supabase Storage to host your TTRPG embedding files, making them available across all deployments without GitHub file size limitations.

## Why Supabase for Embeddings?

✅ **Pros:**

- No file size limits (GitHub has 100MB limit)
- Fast global CDN delivery
- Free tier includes 1GB storage
- Simple REST API integration
- Automatic public URLs
- Version control friendly (no large files in Git)

❌ **Cons:**

- Requires internet connection for fresh deployments
- Small ongoing storage cost after free tier

## Setup Steps

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create account
2. Create new project
3. Note your project URL: `https://your-project-id.supabase.co`

### 2. Get API Keys

1. Go to Project Settings → API
2. Copy your `anon public` key (for downloads)
3. Copy your `service_role` key (for uploads)

### 3. Set Environment Variables

Create or update your `.env` file:

```bash
# Existing OpenAI API key
OPENAI_API_KEY=your-openai-key

# Add Supabase configuration
SUPABASE_PROJECT_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_BUCKET_NAME=ttrpg-embeddings
```

### 4. Upload Your Embeddings (One Time)

```bash
# Generate embeddings if you haven't already
python generate_optimized_embeddings.py

# Upload to Supabase
./scripts/upload_embeddings.sh
```

This creates a public bucket and uploads:

- `dune_optimized.json` (~111MB)
- `the-one-ring_optimized.json` (~6.5MB)
- `mouse-guard_optimized.json` (~53MB)

### 5. Update .gitignore (Recommended)

Add to your `.gitignore` to keep large files out of Git:

```
# Large embedding files (stored in Supabase)
embeddings/*_optimized.json
```

## Usage on New Deployments

### Option 1: Download Pre-generated Embeddings (Fast)

```bash
git clone https://github.com/your-username/mydemerzel-project
cd mydemerzel-project

# Set environment variables
export SUPABASE_PROJECT_URL="https://your-project-id.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"

# Download embeddings
./scripts/download_embeddings.sh

# Start app
python app.py
```

### Option 2: Regenerate Embeddings (Always Fresh)

```bash
git clone https://github.com/your-username/mydemerzel-project
cd mydemerzel-project

# Set OpenAI API key
export OPENAI_API_KEY="your-openai-key"

# Generate fresh embeddings
python generate_optimized_embeddings.py

# Start app
python app.py
```

## Deployment Workflows

### Development Workflow

1. Make changes to documents or embedding generation
2. Run `python generate_optimized_embeddings.py`
3. Run `./scripts/upload_embeddings.sh` to update Supabase
4. Commit code changes (not embedding files)

### Production Deployment

1. Deploy code from Git
2. Set Supabase environment variables
3. Run `./scripts/download_embeddings.sh`
4. Start application

## Cost Estimates

**Supabase Free Tier:**

- 1GB storage (enough for ~6 TTRPG systems)
- 2GB bandwidth per month
- Free forever

**Paid Tier (if needed):**

- $0.021 per GB per month storage
- $0.09 per GB bandwidth
- For 10 TTRPG systems (~2GB): ~$0.05/month

## Troubleshooting

**Download fails:**

```bash
# Check your environment variables
echo $SUPABASE_PROJECT_URL
echo $SUPABASE_ANON_KEY

# Verify bucket exists
curl -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
     "$SUPABASE_PROJECT_URL/storage/v1/bucket"
```

**Upload fails:**

```bash
# Check service key (not anon key)
echo $SUPABASE_SERVICE_KEY

# Ensure you have service_role permissions
```

**File not found:**

```bash
# List files in bucket
curl -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
     "$SUPABASE_PROJECT_URL/storage/v1/object/list/ttrpg-embeddings"
```

## Security Notes

- **Anon key**: Safe to commit to Git (public read access only)
- **Service key**: Keep secret (full admin access)
- **Bucket**: Public read, authenticated write
- **Files**: Publicly accessible via URL (no sensitive data in embeddings)

This setup gives you the best of both worlds: fast deployments with pre-generated embeddings, but also the ability to regenerate fresh embeddings when needed.
