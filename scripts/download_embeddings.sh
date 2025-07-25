#!/bin/bash
# scripts/download_embeddings.sh
# Download pre-generated embeddings from Supabase Storage

# Configuration - set these in your environment or update here
SUPABASE_PROJECT_URL="${SUPABASE_PROJECT_URL:-https://npsuzfgqaykewpndhhmb.supabase.co}"
SUPABASE_ANON_KEY="${SUPABASE_ANON_KEY:-your-anon-key}"
BUCKET_NAME="${SUPABASE_BUCKET_NAME:-ttrpg-embeddings}"
EMBEDDINGS_DIR="embeddings"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Downloading pre-generated embeddings from Supabase...${NC}"

# Create embeddings directory if it doesn't exist
mkdir -p "$EMBEDDINGS_DIR"

# Function to download from Supabase Storage
download_embedding() {
    local file_name="$1"
    local display_name="$2"
    
    echo -e "${YELLOW}📥 Downloading ${display_name} embeddings...${NC}"
    
    # Supabase Storage public URL format
    local download_url="${SUPABASE_PROJECT_URL}/storage/v1/object/public/${BUCKET_NAME}/${file_name}"
    
    if curl -L -f -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
            "${download_url}" -o "${EMBEDDINGS_DIR}/${file_name}"; then
        echo -e "${GREEN}✅ ${display_name} embeddings downloaded successfully${NC}"
        
        # Verify file size
        local file_size=$(stat -f%z "${EMBEDDINGS_DIR}/${file_name}" 2>/dev/null || stat -c%s "${EMBEDDINGS_DIR}/${file_name}" 2>/dev/null || echo "unknown")
        echo -e "   File size: ${file_size} bytes"
    else
        echo -e "${RED}❌ Failed to download ${display_name} embeddings${NC}"
        return 1
    fi
}

# Check if Supabase configuration is provided
if [[ "$SUPABASE_PROJECT_URL" == "https://your-project-id.supabase.co" ]] || [[ -z "$SUPABASE_ANON_KEY" ]]; then
    echo -e "${RED}⚠️  Supabase configuration not found${NC}"
    echo "Please set environment variables:"
    echo "  export SUPABASE_PROJECT_URL='https://your-project-id.supabase.co'"
    echo "  export SUPABASE_ANON_KEY='your-anon-key'"
    echo "  export SUPABASE_BUCKET_NAME='ttrpg-embeddings'"
    echo ""
    echo "Or update the script directly with your Supabase details."
    exit 1
fi

# Download all embedding files
download_embedding "dune_optimized.json" "Dune"
download_embedding "the-one-ring_optimized.json" "The One Ring" 
download_embedding "mouse-guard_optimized.json" "Mouse Guard"

echo ""
echo -e "${GREEN}🎉 All embeddings downloaded successfully!${NC}"
echo -e "${BLUE}🚀 You can now run: python app.py${NC}"
echo ""
echo -e "${YELLOW}📊 Summary:${NC}"
ls -lh "${EMBEDDINGS_DIR}"/*_optimized.json 2>/dev/null || echo "No optimized embeddings found"
