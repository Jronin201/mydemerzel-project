import json
from pathlib import Path

# File path to the embeddings JSON file
embeddings_path = Path("/workspaces/mydemerzel-project/embeddings/test_dune_optimized.json")

# Function to analyze the embeddings file
def analyze_embeddings(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Debugging: Check if the file exists
            if not file_path.exists():
                print(f"Error: File {file_path} does not exist.")
                return

            # Debugging: Add exception handling for JSON loading
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return

        # Debugging: Check if the file is too large to load
        print(f"Attempting to load file: {file_path}")
        print(f"File size: {file_path.stat().st_size / (1024 * 1024):.2f} MB")

        # Debugging: Check if data is loaded
        print("File loaded successfully. Analyzing data...")

        # Extract data
        chunks = data.get("chunks", [])
        embeddings = data.get("embeddings", [])
        tfidf_features = data.get("tfidf_features", [])

        # Analysis
        num_chunks = len(chunks)
        avg_chunk_size = sum(len(chunk) for chunk in chunks) / num_chunks if num_chunks > 0 else 0
        num_embeddings = len(embeddings)
        avg_embedding_size = len(embeddings[0]) if embeddings else 0
        tfidf_size = len(tfidf_features)

        # Check for duplicates in embeddings
        unique_embeddings = len(set(tuple(embed) for embed in embeddings if embed))

        # Print results
        print("--- Embeddings Analysis ---")
        print(f"Number of chunks: {num_chunks}")
        print(f"Average chunk size (characters): {avg_chunk_size:.2f}")
        print(f"Number of embeddings: {num_embeddings}")
        print(f"Average embedding size: {avg_embedding_size} floats")
        print(f"TF-IDF feature size: {tfidf_size}")
        print(f"Unique embeddings: {unique_embeddings}")

        # Check for bloat
        if num_chunks != num_embeddings:
            print("❗ Mismatch: Number of chunks and embeddings do not match!")
        if num_embeddings != unique_embeddings:
            print("❗ Duplicate embeddings detected!")

    except Exception as e:
        print(f"Error analyzing embeddings: {e}")

# Run the analysis
if __name__ == "__main__":
    analyze_embeddings(embeddings_path)
