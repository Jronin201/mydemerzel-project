import json
from pathlib import Path

import tiktoken
from openai import OpenAI

MAX_TOKENS = 750
MODEL = "text-embedding-3-small"


def chunk_text(text: str, encoding: tiktoken.Encoding) -> list[str]:
    tokens = encoding.encode(text)
    chunks = []
    for i in range(0, len(tokens), MAX_TOKENS):
        chunk_tokens = tokens[i: i + MAX_TOKENS]
        chunk = encoding.decode(chunk_tokens)
        chunks.append(chunk)
    return chunks


def main() -> None:
    input_file = Path("documents/dune/dune.txt")
    output_file = Path("embeddings/dune.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    client = OpenAI()
    encoding = tiktoken.get_encoding("cl100k_base")

    with input_file.open("r", encoding="utf-8") as f:
        text = f.read()

    results = []
    for chunk in chunk_text(text, encoding):
        chunk = chunk.strip()
        if not chunk:
            continue
        response = client.embeddings.create(model=MODEL, input=chunk)
        embedding = response.data[0].embedding
        results.append({
            "source": "dune.txt",
            "text": chunk,
            "embedding": embedding,
        })

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
