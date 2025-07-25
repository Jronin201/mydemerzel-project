#!/bin/bash
# scripts/direct_upload.sh
# Direct upload to Supabase using REST API

source .env

echo "🚀 Uploading embeddings to Supabase bucket: $SUPABASE_BUCKET_NAME"
echo "Project: $SUPABASE_PROJECT_URL"

upload_file() {
    local file_path="$1"
    local file_name="$2"
    
    echo "📤 Uploading $file_name..."
    echo "   File size: $(ls -lh "$file_path" | awk '{print $5}')"
    
    # Use upsert to overwrite if exists
    response=$(curl -s -X POST \
        "$SUPABASE_PROJECT_URL/storage/v1/object/$SUPABASE_BUCKET_NAME/$file_name" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
        -H "Content-Type: application/json" \
        -H "x-upsert: true" \
        --data-binary "@$file_path")
    
    echo "   Response: $response"
    
    # Test if upload worked by checking public URL
    echo "   Testing download..."
    public_url="$SUPABASE_PROJECT_URL/storage/v1/object/public/$SUPABASE_BUCKET_NAME/$file_name"
    
    if curl -s -I "$public_url" | grep -q "200 OK"; then
        echo "✅ $file_name uploaded successfully!"
        echo "   Public URL: $public_url"
    else
        echo "❌ Upload verification failed for $file_name"
    fi
    echo ""
}

# Upload all three embedding files
upload_file "embeddings/dune_optimized.json" "dune_optimized.json"
upload_file "embeddings/the-one-ring_optimized.json" "the-one-ring_optimized.json" 
upload_file "embeddings/mouse-guard_optimized.json" "mouse-guard_optimized.json"

echo "🎉 Upload process complete!"
echo ""
echo "🔗 Your public URLs:"
echo "   Dune: $SUPABASE_PROJECT_URL/storage/v1/object/public/$SUPABASE_BUCKET_NAME/dune_optimized.json"
echo "   The One Ring: $SUPABASE_PROJECT_URL/storage/v1/object/public/$SUPABASE_BUCKET_NAME/the-one-ring_optimized.json"
echo "   Mouse Guard: $SUPABASE_PROJECT_URL/storage/v1/object/public/$SUPABASE_BUCKET_NAME/mouse-guard_optimized.json"
