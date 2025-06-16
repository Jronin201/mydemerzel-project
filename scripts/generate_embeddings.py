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
        chunk_tokens = tokens[i : i + MAX_TOKENS]
        chunk = encoding.decode(chunk_tokens)
        chunks.append(chunk)
    return chunks


def main() -> None:
    input_dir = Path("documents/the-one-ring")
    output_dir = Path("embeddings")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "the-one-ring.json"

    client = OpenAI()
    encoding = tiktoken.get_encoding("cl100k_base")

    results = []
    for txt_file in sorted(input_dir.glob("*.txt")):
        with txt_file.open("r", encoding="utf-8") as f:
            text = f.read()
        for chunk in chunk_text(text, encoding):
            chunk = chunk.strip()
            if not chunk:
                continue
            response = client.embeddings.create(model=MODEL, input=chunk)
            embedding = response.data[0].embedding
            results.append({
                "source": txt_file.name,
                "text": chunk,
                "embedding": embedding,
            })

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
