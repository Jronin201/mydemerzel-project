#!/bin/bash
# scripts/download_mouse_guard_only.sh
# Download only Mouse Guard embeddings for troubleshooting

# Configuration from environment or fallback
SUPABASE_PROJECT_URL="${SUPABASE_PROJECT_URL:-https://npsuzfgqaykewpndhhmb.supabase.co}"
SUPABASE_ANON_KEY="${SUPABASE_ANON_KEY:-your-anon-key-here}"
BUCKET_NAME="${SUPABASE_BUCKET_NAME:-ttrpg-embeddings}"
EMBEDDINGS_DIR="embeddings"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐭 Downloading Mouse Guard embeddings only...${NC}"

# Create embeddings directory
mkdir -p "$EMBEDDINGS_DIR"

# Download Mouse Guard with extended timeout and retry
download_mouse_guard() {
    local file_name="mouse-guard_optimized.json"
    local display_name="Mouse Guard"
    local max_retries=3
    local retry_count=0
    
    echo -e "${YELLOW}📥 Downloading ${display_name} embeddings...${NC}"
    echo -e "   File: ${file_name}"
    echo -e "   Expected size: ~53MB"
    
    # Supabase Storage public URL format
    local download_url="${SUPABASE_PROJECT_URL}/storage/v1/object/public/${BUCKET_NAME}/${file_name}"
    echo -e "   URL: ${download_url}"
    
    while [ $retry_count -lt $max_retries ]; do
        echo -e "   Attempt $((retry_count + 1))/${max_retries}..."
        
        if curl -L -f \
                --connect-timeout 30 \
                --max-time 600 \
                --retry 3 \
                --retry-delay 5 \
                -H "Authorization: Bearer ${SUPABASE_ANON_KEY}" \
                "${download_url}" -o "${EMBEDDINGS_DIR}/${file_name}"; then
            
            # Verify file was downloaded and has reasonable size
            if [ -f "${EMBEDDINGS_DIR}/${file_name}" ]; then
                local file_size=$(stat -c%s "${EMBEDDINGS_DIR}/${file_name}" 2>/dev/null || stat -f%z "${EMBEDDINGS_DIR}/${file_name}" 2>/dev/null || echo "0")
                
                if [ "$file_size" -gt 50000000 ]; then  # At least 50MB
                    echo -e "${GREEN}✅ ${display_name} embeddings downloaded successfully${NC}"
                    echo -e "   File size: ${file_size} bytes"
                    return 0
                else
                    echo -e "${RED}⚠️  Downloaded file too small (${file_size} bytes), retrying...${NC}"
                    rm -f "${EMBEDDINGS_DIR}/${file_name}"
                fi
            else
                echo -e "${RED}⚠️  File not created, retrying...${NC}"
            fi
        else
            echo -e "${RED}⚠️  Download failed, retrying...${NC}"
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            echo -e "   Waiting 10 seconds before retry..."
            sleep 10
        fi
    done
    
    echo -e "${RED}❌ Failed to download ${display_name} embeddings after ${max_retries} attempts${NC}"
    return 1
}

# Test connectivity first
echo -e "${BLUE}🔗 Testing connectivity...${NC}"
if curl -s --connect-timeout 10 --max-time 30 "${SUPABASE_PROJECT_URL}/storage/v1/bucket" > /dev/null; then
    echo -e "${GREEN}✅ Connectivity OK${NC}"
else
    echo -e "${RED}❌ Cannot reach Supabase${NC}"
    exit 1
fi

# Download Mouse Guard
if download_mouse_guard; then
    echo -e "${GREEN}🎉 Mouse Guard embeddings ready!${NC}"
    ls -lh "${EMBEDDINGS_DIR}/mouse-guard_optimized.json"
    exit 0
else
    echo -e "${RED}💥 Mouse Guard download failed${NC}"
    exit 1
fi
