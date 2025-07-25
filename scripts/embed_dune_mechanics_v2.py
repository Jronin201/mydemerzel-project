import openai
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import time
from supabase import create_client

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate Supabase configuration
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Service Key is not set. Please check your environment variables.")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# File paths
input_path_dune = Path("/workspaces/mydemerzel-project/documents/dune/dune_mechanics.txt")
output_path_dune = Path("/workspaces/mydemerzel-project/embeddings/dune_mechanics_v2.json")

input_path_mouse_guard = Path("/workspaces/mydemerzel-project/documents/mouse-guard/mouse_guard_mechanics.txt")
output_path_mouse_guard = Path("/workspaces/mydemerzel-project/embeddings/mouse_guard_mechanics_v2.json")

# Load and chunk text
def load_and_chunk_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Simple chunking fallback — split every ~500 words
    words = raw_text.split()
    return [" ".join(words[i:i+500]) for i in range(0, len(words), 500)]

chunks_dune = load_and_chunk_text(input_path_dune)
chunks_mouse_guard = load_and_chunk_text(input_path_mouse_guard)

# Embedding function with retries (new SDK)
def embed_text(text, model="text-embedding-3-small", retries=3):
    for attempt in range(retries):
        try:
            response = openai.Embedding.create(
                input=text,
                model=model
            )
            if isinstance(response, dict) and 'data' in response and len(response['data']) > 0:
                return response['data'][0]['embedding']
            else:
                raise ValueError("Invalid response structure from OpenAI API.")
        except Exception as e:
            print(f"Retry {attempt+1} failed: {e}")
            time.sleep(1.5 * (2 ** attempt))
    print("Failed to embed after 3 attempts.")
    return None

# Generate embeddings
def generate_embeddings(chunks):
    output_data = []
    for i, chunk in enumerate(chunks):
        emb = embed_text(chunk)
        if emb:
            output_data.append({
                "id": i,
                "text": chunk,
                "embedding": emb,
                "tokens": len(chunk.split())
            })
    return output_data

output_data_dune = generate_embeddings(chunks_dune)

# Save to JSON
with open(output_path_dune, "w", encoding="utf-8") as f:
    json.dump(output_data_dune, f, indent=2)

print(f"✅ Saved {len(output_data_dune)} embedded chunks to {output_path_dune}")

# Upload to Supabase

# Upload function
def upload_to_supabase(file_path, bucket_name="embeddings", file_name="dune_mechanics_v2.json"):
    with open(file_path, "rb") as f:
        response = supabase.storage.from_(bucket_name).upload(file_name, f)
        if not response:
            print(f"❌ Failed to upload {file_name}: No response from Supabase.")
        elif isinstance(response, dict) and "error" in response:
            print(f"❌ Failed to upload {file_name}: {response['error']}")
        else:
            print(f"✅ Successfully uploaded {file_name} to Supabase bucket '{bucket_name}'.")

# Call upload function
upload_to_supabase(output_path_dune)

# Process Mouse Guard mechanics

# Generate embeddings for Mouse Guard
output_data_mouse_guard = generate_embeddings(chunks_mouse_guard)

# Save to JSON for Mouse Guard
with open(output_path_mouse_guard, "w", encoding="utf-8") as f:
    json.dump(output_data_mouse_guard, f, indent=2)

print(f"✅ Saved {len(output_data_mouse_guard)} embedded chunks to {output_path_mouse_guard}")

# Call upload function for Mouse Guard
upload_to_supabase(output_path_mouse_guard, file_name="mouse_guard_mechanics_v2.json")
