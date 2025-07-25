# 🚀 Demerzel Project - Developer Quick Reference

**Complete command reference for project management, TTRPG extension, and maintenance**

## ⚡ Ultra-Quick Commands

```bash
# Essential commands for immediate use:
python scripts/show_commands.py                    # Show all available commands
./shortcuts.sh status                             # Project status overview
source shortcuts.sh                               # Load convenient aliases
python scripts/register_ttrpg.py list             # List all TTRPGs
python scripts/test_ttrpg_integration.py          # Test all systems
./deploy.sh                                       # Deploy/restart server
```

## 🎯 Most Common Tasks

### Add New TTRPG (One-liner after sourcing shortcuts)

```bash
source shortcuts.sh
ttrpg-add "shadowrun" "Shadowrun" "Game Master" "Cyberpunk fantasy"
```

### Check Everything is Working

```bash
./shortcuts.sh status              # Quick overview
python scripts/manage_ttrpg.py validate    # Detailed validation
```

---

## 🎮 TTRPG Management Commands

### Registration & Setup

```bash
# Register a new TTRPG (auto-creates all structure)
python scripts/register_ttrpg.py register \
  --name "system-name" \
  --display-name "Display Name" \
  --description "Brief description" \
  --gm-title "Game Master Title" \
  --themes "theme1" "theme2" "theme3" \
  --setting "Setting description"

# List all registered TTRPGs
python scripts/register_ttrpg.py list

# Activate/deactivate TTRPGs
python scripts/register_ttrpg.py activate system-name
python scripts/register_ttrpg.py deactivate system-name
```

### Testing & Validation

```bash
# Test specific TTRPG integration
python scripts/test_ttrpg_integration.py --ttrpg system-name

# Test all active TTRPGs
python scripts/test_ttrpg_integration.py

# Generate detailed test report
python scripts/test_ttrpg_integration.py --ttrpg system-name --report

# Validate all TTRPG configurations
python scripts/manage_ttrpg.py validate

# Validate specific TTRPG
python scripts/manage_ttrpg.py validate --ttrpg system-name
```

### Backup & Maintenance

```bash
# Backup specific TTRPG
python scripts/manage_ttrpg.py backup system-name

# Backup to custom directory
python scripts/manage_ttrpg.py backup system-name --output-dir custom-backups

# Export TTRPG as portable package
python scripts/manage_ttrpg.py export system-name /path/to/export

# Clean inactive TTRPGs (dry run first)
python scripts/manage_ttrpg.py clean
python scripts/manage_ttrpg.py clean --no-dry-run  # Actually remove files
```

### Demonstration & Learning

```bash
# Show extensibility demo
python scripts/demo_extensibility.py demo

# Show current systems overview
python scripts/demo_extensibility.py systems

# Show system features
python scripts/demo_extensibility.py features

# Show file structure guide
python scripts/demo_extensibility.py structure
```

---

## 🖥️ Deployment & Server Management

### Development Server

```bash
# Start development server (fastest)
./start.sh

# Equivalent manual command:
source venv/bin/activate && python app.py
```

### Production Deployment

```bash
# Deploy to production (optimized)
./deploy.sh

# Deploy with development server but production dependencies
./deploy.sh --dev
```

### Health & Monitoring

```bash
# Check if server is running
curl http://localhost:5000/health

# Check server status with details
curl -s http://localhost:5000/health | python -m json.tool
```

---

## 🧠 TTRPG Manual Embedding & Vectorization

### Prerequisites for Embedding New Manuals

```bash
# Ensure OpenAI API key is configured
grep OPENAI_API_KEY .env || echo "OPENAI_API_KEY=your-key-here" >> .env

# Verify embedding tools are available
ls -la *.py | grep -E "(generate_optimized_embeddings|analyze_embeddings|verify_optimization)"
ls -la run_embedding_optimization.sh
```

### 📖 Adding New TTRPG Manual for Embedding

**Step 1: Prepare Document Files**

```bash
# Create document directory for new TTRPG
mkdir -p documents/new-ttrpg-name

# Place source text files in the directory
# Supported formats: .txt files with clean text content
# Example structure:
documents/new-ttrpg-name/
├── core-rules.txt
├── player-handbook.txt
└── gm-guide.txt

# For PDF sources, extract text first:
# Use tools like pdftotext, or manual extraction
pdftotext source.pdf documents/new-ttrpg-name/extracted-text.txt
```

**Step 2: Update Embedding Generation Script**

```bash
# Edit the generation script to include your new TTRPG
nano generate_optimized_embeddings.py

# Add your document to the 'documents' list in main() function:
# {
#     'input': Path("documents/new-ttrpg-name/core-rules.txt"),
#     'output': Path("embeddings/new-ttrpg-name_optimized.json"),
#     'source': 'core-rules.txt'
# }
```

**Step 3: Generate Optimized Embeddings**

```bash
# Run the complete optimization workflow
./run_embedding_optimization.sh

# Or run manually with monitoring:
source .env && python generate_optimized_embeddings.py

# Verify generation was successful
ls -lh embeddings/*new-ttrpg-name*
```

**Step 4: Integrate with Application**

```bash
# Update app.py to load the new embeddings
nano app.py

# Add loading code similar to existing systems:
# new_ttrpg_embeddings = []
# if Path("embeddings/new-ttrpg-name_optimized.json").exists():
#     new_ttrpg_embeddings = load_optimized_embeddings("embeddings/new-ttrpg-name_optimized.json")

# Add search logic in chat() function:
# if page == "new-ttrpg-name" and new_ttrpg_embeddings:
#     context_keywords = ["keyword1", "keyword2", "keyword3"]
#     reference_text = improved_embedding_search(...)
```

### 🔄 Complete Embedding Workflow Command

**One-liner for adding new TTRPG embeddings:**

```bash
# Command structure for adding new TTRPG embeddings:
./scripts/add_ttrpg_embeddings.sh "ttrpg-name" "path/to/documents" "keyword1,keyword2,keyword3"
```

### 📊 Embedding Quality Analysis

**Analyze embedding effectiveness:**

```bash
# Run comprehensive analysis
python analyze_embeddings.py

# Test search performance
python test_optimized_search.py

# Verify integration
python verify_optimization.py
```

**Quality benchmarks to check:**

- Chunk sizes: 100-1000 characters (optimal)
- Similarity scores: >0.3 for good matches
- Coverage: 3+ relevant references per query
- Diversity: No redundant results

### 🎯 Embedding Optimization Parameters

**Key settings in `generate_optimized_embeddings.py`:**

```python
OPTIMAL_CHUNK_SIZE = 500    # Target chunk size in characters
MAX_CHUNK_SIZE = 1000      # Maximum chunk size
MIN_CHUNK_SIZE = 100       # Minimum chunk size
OVERLAP_SIZE = 100         # Overlap between chunks for context
```

**Domain-specific keywords for different TTRPG types:**

```python
# Fantasy: ["magic", "spell", "dungeon", "adventure", "character"]
# Sci-Fi: ["technology", "starship", "planet", "alien", "future"]
# Horror: ["investigation", "sanity", "monster", "mystery", "supernatural"]
# Cyberpunk: ["hacking", "cyberware", "corporate", "street", "matrix"]
```

### 🔍 Testing New Embeddings

**Test queries to verify embedding quality:**

```bash
# Start Flask app with new embeddings
python app.py

# Test in browser or via API:
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I create a character?", "page": "new-ttrpg-name"}'

# Check console for debug output:
# [DEBUG] Added X chars of new-ttrpg-name reference content
# [DEBUG] User embedding generated for new-ttrpg-name: True
```

### 🚀 Production Deployment with New Embeddings

**Deploy with new embeddings:**

```bash
# 1. Generate embeddings locally (not committed to git)
./run_embedding_optimization.sh

# 2. Commit code changes (app.py updates)
git add app.py generate_optimized_embeddings.py
git commit -m "feat: Add embeddings for new-ttrpg-name"
git push

# 3. Deploy and regenerate embeddings on server
./deploy.sh
# Then on server: ./run_embedding_optimization.sh
```

### 🛠️ Embedding Maintenance Commands

**Regular maintenance:**

```bash
# Check embedding file health
python -c "
import json, os
for f in os.listdir('embeddings'):
    if f.endswith('.json'):
        try:
            with open(f'embeddings/{f}') as file:
                data = json.load(file)
                print(f'{f}: {len(data)} chunks, {os.path.getsize(f\"embeddings/{f}\")/1024/1024:.1f}MB')
        except Exception as e:
            print(f'{f}: ERROR - {e}')
"

# Regenerate all embeddings
./run_embedding_optimization.sh

# Update specific TTRPG embeddings
python generate_optimized_embeddings.py --ttrpg specific-name

# Clean up old embedding files
rm embeddings/*_old.json
```

### 📝 Quick Command Reference for Embeddings

```bash
# Essential embedding commands:
./run_embedding_optimization.sh              # Generate all optimized embeddings
python analyze_embeddings.py                 # Analyze embedding quality
python test_optimized_search.py             # Test search performance
python verify_optimization.py               # Verify integration works

# Embedding file management:
ls -lh embeddings/                          # Check embedding files
grep -r "embeddings.*json" app.py           # Find embedding usage in code
git status | grep embeddings                # Check if embeddings in git (should be empty)

# Troubleshooting:
tail -f flask_app.log | grep DEBUG          # Monitor embedding search
curl -s http://localhost:5000/health        # Check if app loads embeddings
```

**💡 Pro Tips for Embeddings:**

- Always test with representative queries after adding new embeddings
- Monitor similarity scores in console logs (aim for >0.3)
- Use domain-specific keywords for better context-aware search
- Chunk sizes of 100-1000 chars work best for TTRPG content
- Include overlap between chunks to preserve context
- Regenerate embeddings when documents are updated significantly

---

## 🛠️ Project Maintenance Commands

### Backup & Security

```bash
# Create full project backup
./backup.sh

# Run security audit
./security_check.sh

# Manual backup with timestamp
tar -czf "backup_$(date +%Y%m%d_%H%M%S).tar.gz" \
  --exclude='venv' --exclude='__pycache__' \
  --exclude='.git' --exclude='node_modules' .
```

### Testing & Quality Assurance

```bash
# Run all TTRPG tests
python scripts/test_ttrpg_integration.py

# Test specific functionality
python test_character_persistence.py
python test_system_prompts.py
python test_comprehensive_ttrpg.py

# Validate project health
python scripts/manage_ttrpg.py validate
```

### Data Management

```bash
# Check embeddings
ls -la embeddings/

# Regenerate embeddings for TTRPG (if you have the script)
python scripts/generate_embeddings.py --ttrpg system-name

# View current TTRPG configuration
cat ttrpg-config.json | python -m json.tool

# Check user data structure
ls -la character_info/anonymous/
ls -la chat_histories/anonymous/
```

---

## 📝 File Editing Quick Commands

### TTRPG System Prompts

```bash
# Edit system prompt for specific TTRPG
nano static/system-name/system_prompt.txt

# View existing system prompt
cat static/system-name/system_prompt.txt

# Compare system prompts
diff static/dune/system_prompt.txt static/call-of-cthulhu/system_prompt.txt
```

### Configuration Files

```bash
# Edit main TTRPG configuration
nano ttrpg-config.json

# Edit environment variables
nano .env

# Edit deployment configuration
nano deploy.sh
nano start.sh
```

### Documentation

```bash
# Edit main extension guide
nano docs/TTRPG_EXTENSION_GUIDE.md

# Edit quick reference
nano docs/TTRPG_QUICK_REFERENCE.md

# Edit deployment guide
nano DEPLOYMENT.md
```

---

## 🔍 Diagnostic & Debugging Commands

### Log Analysis

```bash
# View recent terminal output
python -c "
import glob, os
files = glob.glob('diagnostics/*')
if files:
    latest = max(files, key=os.path.getctime)
    print(f'Latest diagnostic: {latest}')
    with open(latest) as f: print(f.read()[-2000:])
"

# Check for errors in logs
grep -i error diagnostics/* 2>/dev/null || echo "No error logs found"
```

### System Status

```bash
# Check Python environment
python --version
pip list | grep -E "(flask|openai|requests)"

# Check file permissions
ls -la *.sh scripts/*.py

# Check port availability
netstat -tlnp | grep :5000 || echo "Port 5000 available"
```

### Quick Diagnostics

```bash
# One-command health check
echo "=== SYSTEM HEALTH CHECK ===" && \
python --version && \
echo "Server status:" && curl -s http://localhost:5000/health && \
echo -e "\nActive TTRPGs:" && python scripts/register_ttrpg.py list | grep "Active" && \
echo -e "\nValidation:" && python scripts/manage_ttrpg.py validate
```

---

## 🎯 Common Workflows

### Adding a New TTRPG (Complete Workflow)

```bash
# 1. Register
python scripts/register_ttrpg.py register --name "new-system" --display-name "New System"

# 2. Edit system prompt
nano static/new-system/system_prompt.txt

# 3. Test
python scripts/test_ttrpg_integration.py --ttrpg new-system

# 4. Deploy
./deploy.sh

# 5. Verify
curl http://localhost:5000/new-system
```

### Troubleshooting a TTRPG

```bash
# 1. Validate configuration
python scripts/manage_ttrpg.py validate --ttrpg system-name

# 2. Test integration
python scripts/test_ttrpg_integration.py --ttrpg system-name

# 3. Check system prompt
cat static/system-name/system_prompt.txt

# 4. Verify registration
python scripts/register_ttrpg.py list | grep system-name

# 5. Check server logs
curl -s http://localhost:5000/health
```

### Updating System Prompts

```bash
# 1. Backup current prompt
cp static/system-name/system_prompt.txt static/system-name/system_prompt.txt.backup

# 2. Edit prompt
nano static/system-name/system_prompt.txt

# 3. Validate
python scripts/manage_ttrpg.py validate --ttrpg system-name

# 4. Test
python scripts/test_ttrpg_integration.py --ttrpg system-name

# 5. No restart needed - changes are live!
```

### Project Backup & Recovery

```bash
# 1. Full backup
./backup.sh

# 2. TTRPG-specific backup
python scripts/manage_ttrpg.py backup system-name

# 3. Export for migration
python scripts/manage_ttrpg.py export system-name /path/to/package

# 4. Verify backup integrity
tar -tzf backup_*.tar.gz | head -20
```

---

## 📚 Documentation Quick Access

```bash
# View complete extension guide
less docs/TTRPG_EXTENSION_GUIDE.md

# View quick reference
less docs/TTRPG_QUICK_REFERENCE.md

# View deployment guide
less DEPLOYMENT.md

# Show all documentation files
find docs/ -name "*.md" -exec echo "=== {} ===" \; -exec head -5 {} \;
```

---

## 🎮 Advanced TTRPG Features

### Custom Templates

```bash
# Copy master template
cp -r static/master-template static/new-system-template

# Create from existing TTRPG
python scripts/manage_ttrpg.py export existing-system /tmp/template
# Then modify and register as new system
```

### Bulk Operations

```bash
# Test all TTRPGs
python scripts/test_ttrpg_integration.py

# Validate all
python scripts/manage_ttrpg.py validate

# Backup all active systems
for system in $(python scripts/register_ttrpg.py list | grep "Active" | awk '{print $NF}' | tr -d '()'); do
    python scripts/manage_ttrpg.py backup "$system"
done
```

---

**💡 Pro Tips:**

- Always run `python scripts/test_ttrpg_integration.py` before deploying
- Use `./backup.sh` before major changes
- The `--help` flag works on all scripts for detailed options
- Changes to system prompts are live - no restart needed
- Use `python scripts/demo_extensibility.py systems` for quick status overview

---

## 🧠 Embedding/Vectorization Workflow for New TTRPG Manuals

### Automated Script (Recommended)

For easy addition of new TTRPGs with optimal embeddings:

```bash
# Basic usage
./scripts/add_ttrpg_embeddings.sh <ttrpg-name> <documents-path> <keywords>

# Example for Shadowrun
./scripts/add_ttrpg_embeddings.sh shadowrun documents/shadowrun "cyberware,hacking,corporate,street"

# Example for Call of Cthulhu
./scripts/add_ttrpg_embeddings.sh cthulhu documents/cthulhu "investigator,sanity,mythos,horror"
```

The script automatically:

- Validates prerequisites (API key, source files)
- Updates embedding generation with new documents
- Generates optimized embeddings with semantic chunking
- Integrates search logic into app.py
- Verifies the integration works correctly
- Provides testing recommendations

### Manual Integration Steps

For direct control over the embedding process:

1. **Prepare source documents**: Place .txt files in `documents/[ttrpg-name]/`
2. **Update embedding generation**: Modify `generate_optimized_embeddings.py` to include new document paths
3. **Generate embeddings**: Run `python generate_optimized_embeddings.py`
4. **Update app.py**: Add loading and search logic for the new TTRPG
5. **Test integration**: Verify embeddings work correctly with test queries

This ensures consistent, high-quality embedding and search functionality for any future TTRPG manual additions.

### Deployment with Supabase Storage

For production deployments, use Supabase to host large embedding files:

```bash
# One-time setup: Upload embeddings to Supabase
./scripts/upload_embeddings.sh

# Deployment: Download embeddings from Supabase
./scripts/download_embeddings.sh

# Verify integration
python verify_optimization.py
```

**Environment variables needed:**

```bash
SUPABASE_PROJECT_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key  # for uploads only
SUPABASE_BUCKET_NAME=ttrpg-embeddings
```

**Benefits:**

- ✅ No GitHub file size limits
- ✅ Fast deployment (no regeneration)
- ✅ Works on locked computers
- ✅ Free tier sufficient for most use

See `docs/SUPABASE_EMBEDDING_SETUP.md` for complete setup guide.

---
