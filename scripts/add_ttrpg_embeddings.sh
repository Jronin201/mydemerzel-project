#!/bin/bash
# scripts/add_ttrpg_embeddings.sh
# Automated script for adding embeddings for new TTRPG manuals

set -e  # Exit on any error

TTRPG_NAME="$1"
DOCUMENTS_PATH="$2" 
KEYWORDS="$3"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Help function
show_help() {
    echo -e "${BLUE}🧠 Add TTRPG Embeddings Script${NC}"
    echo "Usage: $0 <ttrpg-name> <documents-path> <keywords>"
    echo ""
    echo "Parameters:"
    echo "  ttrpg-name     : Name for the TTRPG system (e.g., 'shadowrun')"
    echo "  documents-path : Path to directory containing .txt documents"
    echo "  keywords       : Comma-separated keywords for context boosting"
    echo ""
    echo "Example:"
    echo "  $0 shadowrun documents/shadowrun 'cyberware,hacking,corporate,street'"
    echo ""
    echo "Prerequisites:"
    echo "  - OpenAI API key in .env file"
    echo "  - Source documents in .txt format"
    echo "  - Embedding generation tools available"
}

# Validate parameters
if [ $# -ne 3 ]; then
    show_help
    exit 1
fi

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

echo -e "${BLUE}🧠 ADDING TTRPG EMBEDDINGS: ${TTRPG_NAME}${NC}"
echo "=================================================="

# Validate prerequisites
echo -e "${YELLOW}📋 Validating prerequisites...${NC}"

# Check for .env file with API key
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Create .env file with OPENAI_API_KEY=your-key-here"
    exit 1
fi

if ! grep -q "OPENAI_API_KEY" .env; then
    echo -e "${RED}❌ OPENAI_API_KEY not found in .env${NC}"
    exit 1
fi

# Check if documents directory exists
if [ ! -d "$DOCUMENTS_PATH" ]; then
    echo -e "${RED}❌ Documents directory not found: $DOCUMENTS_PATH${NC}"
    exit 1
fi

# Check for .txt files in documents directory
txt_files=$(find "$DOCUMENTS_PATH" -name "*.txt" | wc -l)
if [ "$txt_files" -eq 0 ]; then
    echo -e "${RED}❌ No .txt files found in $DOCUMENTS_PATH${NC}"
    echo "Please add source text files (.txt format) to the documents directory"
    exit 1
fi

echo -e "${GREEN}✅ Found $txt_files .txt files in $DOCUMENTS_PATH${NC}"

# Check for required scripts
required_scripts=("generate_optimized_embeddings.py" "analyze_embeddings.py" "verify_optimization.py")
for script in "${required_scripts[@]}"; do
    if [ ! -f "$script" ]; then
        echo -e "${RED}❌ Required script not found: $script${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ All required scripts available${NC}"

# Step 1: Update embedding generation script
echo -e "${YELLOW}🔧 Step 1: Updating embedding generation script...${NC}"

# Create backup
cp generate_optimized_embeddings.py generate_optimized_embeddings.py.backup

# Add document entries to the generation script
echo -e "${BLUE}📝 Adding documents to generation script:${NC}"
find "$DOCUMENTS_PATH" -name "*.txt" | while read -r txt_file; do
    filename=$(basename "$txt_file")
    echo "   • $filename → embeddings/${TTRPG_NAME}_optimized.json"
done

# Create a temporary modification script
cat > /tmp/update_embeddings.py << EOF
import re

# Read the current script
with open('generate_optimized_embeddings.py', 'r') as f:
    content = f.read()

# Find the documents list in main() function
# Look for the pattern where documents are defined
documents_pattern = r'(documents = \[.*?\])'
match = re.search(documents_pattern, content, re.DOTALL)

if match:
    current_docs = match.group(1)
    
    # Add new documents
    new_docs = []
    import glob
    for txt_file in glob.glob('${DOCUMENTS_PATH}/*.txt'):
        filename = txt_file.split('/')[-1]
        new_doc = '''        {
            'input': Path("${txt_file}"),
            'output': Path("embeddings/${TTRPG_NAME}_optimized.json"),
            'source': '${filename}'
        }'''
        new_docs.append(new_doc)
    
    if new_docs:
        # Insert before the closing bracket
        insertion_point = current_docs.rfind(']')
        if current_docs.strip().endswith('[]'):
            # Empty list
            new_content = current_docs[:-1] + ',\n'.join(new_docs) + '\n    ]'
        else:
            # Add comma and new entries
            new_content = current_docs[:insertion_point] + ',\n' + ',\n'.join(new_docs) + '\n    ]'
        
        # Replace in content
        content = content.replace(current_docs, new_content)
        
        # Write back
        with open('generate_optimized_embeddings.py', 'w') as f:
            f.write(content)
        
        print("✅ Added ${TTRPG_NAME} documents to generation script")
    else:
        print("⚠️  No .txt files found to add")
else:
    print("❌ Could not find documents list in generation script")
    print("Please manually add your documents to the 'documents' list in main()")
EOF

python /tmp/update_embeddings.py
rm /tmp/update_embeddings.py

# Step 2: Generate embeddings
echo -e "${YELLOW}🚀 Step 2: Generating optimized embeddings...${NC}"
echo "This may take several minutes depending on document size..."

source .env
if ! python generate_optimized_embeddings.py; then
    echo -e "${RED}❌ Embedding generation failed${NC}"
    echo "Restoring backup..."
    mv generate_optimized_embeddings.py.backup generate_optimized_embeddings.py
    exit 1
fi

# Step 3: Update app.py with new embedding integration
echo -e "${YELLOW}🔧 Step 3: Updating app.py integration...${NC}"

# Create backup
cp app.py app.py.backup

# Add loading code for new embeddings
cat >> /tmp/app_updates.py << EOF
import re

# Read app.py
with open('app.py', 'r') as f:
    content = f.read()

# Add loading code after existing embedding loads
loading_code = '''
# Load ${TTRPG_NAME} embeddings (prefer optimized version)
${TTRPG_NAME}_embeddings = []
optimized_${TTRPG_NAME}_path = "embeddings/${TTRPG_NAME}_optimized.json"
fallback_${TTRPG_NAME}_path = "embeddings/${TTRPG_NAME}.json"

if Path(optimized_${TTRPG_NAME}_path).exists():
    ${TTRPG_NAME}_embeddings = load_optimized_embeddings(optimized_${TTRPG_NAME}_path)
    print("📚 Loaded optimized ${TTRPG_NAME} embeddings")
elif Path(fallback_${TTRPG_NAME}_path).exists():
    ${TTRPG_NAME}_embeddings = load_optimized_embeddings(fallback_${TTRPG_NAME}_path)
    print("📚 Loaded standard ${TTRPG_NAME} embeddings")
'''

# Find where to insert (after existing embedding loads)
insertion_point = content.find('# --- Enhanced TTRPG Configuration Management ---')
if insertion_point != -1:
    content = content[:insertion_point] + loading_code + '\n' + content[insertion_point:]
else:
    print("⚠️  Could not find insertion point for loading code")
    print("Please manually add the loading code to app.py")

# Add search logic in chat function
search_code = '''
    # Enhanced ${TTRPG_NAME} embedding search
    if page == "${TTRPG_NAME}" and ${TTRPG_NAME}_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated for ${TTRPG_NAME}:", bool(user_embedding))

            # Use improved search with multiple results and context awareness
            context_keywords = ["${KEYWORDS}".replace(",", '", "').split('", "')]
            reference_text = improved_embedding_search(
                query=user_input,
                query_embedding=user_embedding,
                embeddings=${TTRPG_NAME}_embeddings,
                ttrpg_type="${TTRPG_NAME}",
                context_keywords=context_keywords
            )
            
            if reference_text:
                full_system_prompt += (
                    f"\\n\\n[RELEVANT EXCERPTS FROM ${TTRPG_NAME.upper()} RULES]\\n"
                    f"Do not reveal or quote these unless the user explicitly asks:\\n{reference_text}"
                )
                print(f"[DEBUG] Added {len(reference_text)} chars of ${TTRPG_NAME} reference content")
            
        except Exception as e:
            print("${TTRPG_NAME} embedding search failed:", e)
'''

# Find where to insert search logic (before the OpenAI API call)
search_insertion = content.find('    from openai.types.chat import (')
if search_insertion != -1:
    content = content[:search_insertion] + search_code + '\n' + content[search_insertion:]
else:
    print("⚠️  Could not find insertion point for search code")
    print("Please manually add the search code to the chat() function in app.py")

# Write updated content
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Updated app.py with ${TTRPG_NAME} integration")
EOF

python /tmp/app_updates.py
rm /tmp/app_updates.py

# Step 4: Verify integration
echo -e "${YELLOW}🧪 Step 4: Verifying integration...${NC}"

if ! python verify_optimization.py; then
    echo -e "${RED}❌ Integration verification failed${NC}"
    echo "Restoring backups..."
    mv app.py.backup app.py
    mv generate_optimized_embeddings.py.backup generate_optimized_embeddings.py
    exit 1
fi

# Step 5: Analyze embedding quality
echo -e "${YELLOW}📊 Step 5: Analyzing embedding quality...${NC}"
python analyze_embeddings.py | grep -A 20 "${TTRPG_NAME}"

# Cleanup backups if everything succeeded
rm -f app.py.backup generate_optimized_embeddings.py.backup

echo -e "${GREEN}🎉 SUCCESS! ${TTRPG_NAME} embeddings added successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Test the integration:"
echo "   python app.py"
echo "   # Visit your TTRPG page and test queries"
echo ""
echo "2. Monitor debug output for:"
echo "   [DEBUG] Added X chars of ${TTRPG_NAME} reference content"
echo ""
echo "3. Test with representative queries:"
echo "   - Character creation rules"
echo "   - Core mechanics"
echo "   - Setting-specific information"
echo ""
echo "4. Commit your changes:"
echo "   git add app.py generate_optimized_embeddings.py"
echo "   git commit -m \"feat: Add ${TTRPG_NAME} embeddings integration\""
echo ""
echo -e "${GREEN}✅ Your AI should now provide enhanced responses for ${TTRPG_NAME} queries!${NC}"
