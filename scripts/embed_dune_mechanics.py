import openai
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
from dotenv import load_dotenv
import os
from scipy.sparse import spmatrix, issparse
import requests

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# File paths
dune_mechanics_path = Path("/workspaces/mydemerzel-project/documents/dune/dune_mechanics.txt")
output_path = Path("/workspaces/mydemerzel-project/embeddings/dune_optimized.json")

# Read the Dune_Mechanics.txt file
with open(dune_mechanics_path, "r", encoding="utf-8") as file:
    dune_text = file.read()

# Split the text into chunks (e.g., paragraphs)
chunks = dune_text.split("\n\n")

# Updated generate_embeddings function to handle API response correctly using `response['data']`
def generate_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        try:
            response = openai.Embedding.create(
                input=chunk,
                model="text-embedding-ada-002"
            )
            # Access the embedding from the response data
            embedding = response["data"][0]["embedding"]
            embeddings.append(embedding)
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error accessing embedding for chunk: {chunk[:30]}... - {e}")
            embeddings.append([])  # Append empty embedding on error
        except Exception as e:
            print(f"Error generating embedding for chunk: {chunk[:30]}... - {e}")
            embeddings.append([])  # Append empty embedding on error
    return embeddings

# Vectorize the text using TF-IDF for additional metadata
def vectorize_text(chunks):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunks)
    return tfidf_matrix

# Generate embeddings and vectorize text
embeddings = generate_embeddings(chunks)
tfidf_matrix = vectorize_text(chunks)

# Fix for tfidf_matrix
# Convert sparse matrix to dense if necessary
if issparse(tfidf_matrix):
    tfidf_matrix = tfidf_matrix.toarray()
else:
    tfidf_matrix = tfidf_matrix.tolist()

# Combine embeddings and metadata into a JSON structure
output_data = {
    "chunks": chunks,
    "embeddings": embeddings,
    "tfidf_features": tfidf_matrix.tolist()
}

# Upload embeddings to Supabase
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def upload_to_supabase(file_path, bucket_name, file_name):
    if not SUPABASE_PROJECT_URL or not SUPABASE_SERVICE_KEY:
        print("Supabase configuration is missing in the .env file.")
        return False

    upload_url = f"{SUPABASE_PROJECT_URL}/storage/v1/object/{bucket_name}/{file_name}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "X-Upsert": "true"
    }

    with open(file_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f)
        if response.status_code == 200:
            print(f"✅ Successfully uploaded {file_name} to Supabase.")
            return True
        else:
            print(f"❌ Failed to upload {file_name} to Supabase: {response.text}")
            return False

# Save the embeddings to a JSON file
with open(output_path, "w", encoding="utf-8") as output_file:
    json.dump(output_data, output_file, indent=2)

print(f"Embeddings saved to {output_path}")

# Upload the file to Supabase
upload_to_supabase(output_path, SUPABASE_BUCKET_NAME, output_path.name)
