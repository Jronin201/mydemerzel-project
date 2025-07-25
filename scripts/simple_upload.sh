#!/bin/bash
# scripts/simple_upload.sh
# Simple upload script using curl directly

SUPABASE_URL="${SUPABASE_PROJECT_URL:-https://npsuzfgqaykewpndhhmb.supabase.co}"
SUPABASE_KEY="${SUPABASE_SERVICE_KEY:-your-service-key-here}"
BUCKET="ttrpg-embeddings"

echo "🚀 Uploading to Supabase manually..."

# Check if service key is set
if [[ "$SUPABASE_KEY" == "your-service-key-here" ]]; then
    echo "❌ SUPABASE_SERVICE_KEY environment variable not set"
    echo "Please set your Supabase service role key:"
    echo "  export SUPABASE_SERVICE_KEY='your-service-key'"
    exit 1
fi

# Upload files using curl POST
for file in embeddings/dune_optimized.json embeddings/the-one-ring_optimized.json embeddings/mouse-guard_optimized.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "📤 Uploading $filename..."
        
        curl -X POST \
            "$SUPABASE_URL/storage/v1/object/$BUCKET/$filename" \
            -H "Authorization: Bearer $SUPABASE_KEY" \
            -H "Content-Type: application/json" \
            --data-binary "@$file"
        
        echo "✅ $filename uploaded"
        echo "🔗 URL: $SUPABASE_URL/storage/v1/object/public/$BUCKET/$filename"
        echo ""
    fi
done
