#!/bin/bash
# scripts/upload_embeddings.sh
# Upload generated embeddings to Supabase Storage

# Configuration - set these in your environment or update here
SUPABASE_PROJECT_URL="${SUPABASE_PROJECT_URL:-https://your-project-id.supabase.co}"
SUPABASE_SERVICE_KEY="${SUPABASE_SERVICE_KEY:-your-service-role-key}"
BUCKET_NAME="${SUPABASE_BUCKET_NAME:-ttrpg-embeddings}"
EMBEDDINGS_DIR="embeddings"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Uploading embeddings to Supabase Storage...${NC}"

# Function to upload to Supabase Storage
upload_embedding() {
    local file_path="$1"
    local file_name="$2"
    local display_name="$3"
    
    if [[ ! -f "$file_path" ]]; then
        echo -e "${RED}❌ File not found: $file_path${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}📤 Uploading ${display_name} embeddings...${NC}"
    
    # Get file size for progress info
    local file_size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null || echo "unknown")
    echo -e "   File size: ${file_size} bytes"
    
    # Upload to Supabase Storage
    local upload_url="${SUPABASE_PROJECT_URL}/storage/v1/object/${BUCKET_NAME}/${file_name}"
    
    if curl -X POST \
            -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
            -H "Content-Type: application/json" \
            -H "X-Upsert: true" \
            --data-binary "@${file_path}" \
            "${upload_url}"; then
        echo -e "${GREEN}✅ ${display_name} embeddings uploaded successfully${NC}"
        
        # Generate public URL
        local public_url="${SUPABASE_PROJECT_URL}/storage/v1/object/public/${BUCKET_NAME}/${file_name}"
        echo -e "   Public URL: ${public_url}"
    else
        echo -e "${RED}❌ Failed to upload ${display_name} embeddings${NC}"
        return 1
    fi
    echo ""
}

# Check if Supabase configuration is provided
if [[ "$SUPABASE_PROJECT_URL" == "https://your-project-id.supabase.co" ]] || [[ -z "$SUPABASE_SERVICE_KEY" ]]; then
    echo -e "${RED}⚠️  Supabase configuration not found${NC}"
    echo "Please set environment variables:"
    echo "  export SUPABASE_PROJECT_URL='https://your-project-id.supabase.co'"
    echo "  export SUPABASE_SERVICE_KEY='your-service-role-key'"
    echo "  export SUPABASE_BUCKET_NAME='ttrpg-embeddings'"
    echo ""
    echo "Or update the script directly with your Supabase details."
    exit 1
fi

# Check if bucket exists and create if needed
echo -e "${BLUE}🔧 Ensuring bucket exists...${NC}"
bucket_check_url="${SUPABASE_PROJECT_URL}/storage/v1/bucket/${BUCKET_NAME}"
if ! curl -s -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" "${bucket_check_url}" | grep -q "name"; then
    echo -e "${YELLOW}📦 Creating bucket: ${BUCKET_NAME}${NC}"
    curl -X POST \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"id\":\"${BUCKET_NAME}\",\"name\":\"${BUCKET_NAME}\",\"public\":true}" \
        "${SUPABASE_PROJECT_URL}/storage/v1/bucket"
    echo ""
fi

echo -e "${BLUE}📁 Available embedding files:${NC}"
ls -lh "${EMBEDDINGS_DIR}"/*_optimized.json 2>/dev/null || {
    echo -e "${RED}No optimized embedding files found in ${EMBEDDINGS_DIR}/${NC}"
    echo "Run 'python generate_optimized_embeddings.py' first"
    exit 1
}
echo ""

# Upload all optimized embedding files
upload_embedding "${EMBEDDINGS_DIR}/dune_optimized.json" "dune_optimized.json" "Dune"
upload_embedding "${EMBEDDINGS_DIR}/the-one-ring_optimized.json" "the-one-ring_optimized.json" "The One Ring"
upload_embedding "${EMBEDDINGS_DIR}/mouse-guard_optimized.json" "mouse-guard_optimized.json" "Mouse Guard"

echo -e "${GREEN}🎉 All embeddings uploaded to Supabase successfully!${NC}"
echo ""
echo -e "${BLUE}🔗 Public URLs:${NC}"
echo "   Dune: ${SUPABASE_PROJECT_URL}/storage/v1/object/public/${BUCKET_NAME}/dune_optimized.json"
echo "   The One Ring: ${SUPABASE_PROJECT_URL}/storage/v1/object/public/${BUCKET_NAME}/the-one-ring_optimized.json"
echo "   Mouse Guard: ${SUPABASE_PROJECT_URL}/storage/v1/object/public/${BUCKET_NAME}/mouse-guard_optimized.json"
echo ""
echo -e "${YELLOW}💡 To use on other deployments:${NC}"
echo "   1. Set your Supabase environment variables"
echo "   2. Run: ./scripts/download_embeddings.sh"
echo "   3. Start your app: python app.py"
