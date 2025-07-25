# 📁 Embedding Files Information

## 🚨 Important Note About Large Files

The optimized embedding files (`*_optimized.json`) and original embedding files (`*.json`) are **excluded from the repository** because they exceed GitHub's 100MB file size limit.

## 🔄 How to Regenerate Embedding Files

### Prerequisites:

1. Ensure you have an OpenAI API key in your `.env` file:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   ```

### Quick Regeneration:

```bash
# Run the optimization script
./run_embedding_optimization.sh
```

This will generate:

- `embeddings/dune_optimized.json` (~111MB, 2,628 chunks)
- `embeddings/the-one-ring_optimized.json` (~6.5MB, 153 chunks)

### Manual Process:

```bash
# Load environment variables and run optimization
source .env
python generate_optimized_embeddings.py
```

## 📊 What These Files Contain

- **Original files**: Large chunks (~3000 chars each) from the old system
- **Optimized files**: Smaller, semantic chunks (~600 chars each) for better AI search
- **Improvement**: 4.5x more chunks with better granularity and overlapping context

## 🔧 First Time Setup

If you're setting up this project for the first time:

1. Copy your OpenAI API key to `.env`:

   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. Generate the embedding files:

   ```bash
   ./run_embedding_optimization.sh
   ```

3. Start the application:
   ```bash
   python app.py
   ```

The application will automatically detect and use the optimized embedding files for enhanced AI search performance.
