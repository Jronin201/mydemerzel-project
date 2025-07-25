#!/bin/bash
# scripts/check_supabase_files.sh
# Check what files are available in a Supabase project

echo "🔍 Checking Supabase project files..."

# Check if environment variables are set
if [[ -z "$SUPABASE_PROJECT_URL" ]]; then
    echo "❌ SUPABASE_PROJECT_URL environment variable not set"
    echo "Using default project URL for npsuzfgqaykewpndhhmb..."
    SUPABASE_PROJECT_URL="https://npsuzfgqaykewpndhhmb.supabase.co"
fi

if [[ -z "$SUPABASE_ANON_KEY" ]]; then
    echo "❌ SUPABASE_ANON_KEY environment variable not set"
    echo "Please set your Supabase anonymous key"
    exit 1
fi

BUCKET_NAME="${SUPABASE_BUCKET_NAME:-ttrpg-embeddings}"

echo "📡 Checking project: $SUPABASE_PROJECT_URL"
echo "🪣 Bucket: $BUCKET_NAME"
echo ""

# List all files in the bucket
echo "📋 Listing all files in bucket..."
curl -s -X GET \
  "$SUPABASE_PROJECT_URL/storage/v1/object/list/$BUCKET_NAME" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "🔍 Looking for specific embedding files..."

# Check for specific files
FILES=(
    "the-one-ring_optimized.json"
    "the-one-ring.json"
    "dune_optimized.json"  
    "dune.json"
    "mouse-guard_optimized.json"
    "mouse-guard.json"
)

for file in "${FILES[@]}"; do
    echo -n "  $file: "
    response=$(curl -s -o /dev/null -w "%{http_code}" -X HEAD \
        "$SUPABASE_PROJECT_URL/storage/v1/object/$BUCKET_NAME/$file" \
        -H "Authorization: Bearer $SUPABASE_ANON_KEY")
    
    if [[ "$response" == "200" ]]; then
        echo "✅ EXISTS"
    else
        echo "❌ NOT FOUND (HTTP $response)"
    fi
done

echo ""
echo "💡 If files are missing, you may need to upload them or check the bucket name."
