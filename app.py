from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request
import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
from token_counter import count_tokens
from message_history import load_messages_from_file, save_messages_to_file
import numpy as np
from pathlib import Path
import json
import tiktoken

app = Flask(__name__, static_folder="static")
# Explicitly allow cross-origin requests from any domain to fix frontend CORS errors
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
def root():
    return app.send_static_file("index.html")


@app.route("/the-one-ring")
def the_one_ring():
    return app.send_static_file("the-one-ring/index.html")


@app.route("/call-of-cthulhu")
def call_of_cthulhu():
    return app.send_static_file("call-of-cthulhu/index.html")


@app.route("/master-template")
def master_template():
    return app.send_static_file("master-template/index.html")


# Load environment variables and OpenAI client
load_dotenv()
client = OpenAI()


def load_system_prompt(page: str) -> str:
    """Load base prompt and optional page-specific prompt."""
    base_path = Path("system_prompt.txt")
    base_prompt = base_path.read_text(encoding="utf-8").strip() if base_path.exists() else ""

    if page:
        page_paths = [Path("static") / page / "system_prompt.txt", Path("system_prompts") / f"{page}.txt"]
        for p in page_paths:
            if p.exists():
                page_prompt = p.read_text(encoding="utf-8").strip()
                return base_prompt + "\n" + page_prompt if base_prompt else page_prompt

    return base_prompt


TOKEN_THRESHOLD = 150
messages = load_messages_from_file()

# Load embeddings for The One Ring at startup
the_one_ring_embeddings = []
if Path("embeddings/the-one-ring.json").exists():
    with open("embeddings/the-one-ring.json", "r", encoding="utf-8") as f:
        the_one_ring_embeddings = json.load(f)

# Preload reference texts for The One Ring on startup
the_one_ring_texts = {}
tor_dir = os.path.join(app.static_folder, "text", "the-one-ring")
if os.path.isdir(tor_dir):
    for fname in os.listdir(tor_dir):
        if fname.endswith(".txt"):
            with open(os.path.join(tor_dir, fname), "r", encoding="utf-8") as f:
                the_one_ring_texts[fname] = f.read()


def summarize_messages(messages):
    to_summarize = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
    summary_prompt = [
        {
            "role": "system",
            "content": "Summarize the following RPG conversation so far in a concise but detailed paragraph. Focus on world events, decisions made, and NPC interactions. Be specific.",
        }
    ] + to_summarize
    response = client.chat.completions.create(
        model="gpt-4o", messages=summary_prompt
    )
    summary = response.choices[0].message.content.strip()
    return [{"role": "system", "content": f"SUMMARY OF EARLIER CHAT: {summary}"}]


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@app.route("/chat", methods=["POST"])
@cross_origin()  # explicitly allow all origins
def chat():
    global messages
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    user_input = data.get("message", "").strip()

    page = data.get("page") or ""
    if not page:
        ref = request.headers.get("Referer", "")
        if "the-one-ring" in ref:
            page = "the-one-ring"

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages.append({"role": "user", "content": user_input, "timestamp": timestamp})

    if user_input == "?":
        help_text = "**Available Commands:**\n- `?` – Show this help menu"
        messages.append(
            {"role": "assistant", "content": help_text, "timestamp": timestamp}
        )
        save_messages_to_file(messages)
        return jsonify({"response": help_text})

    filtered = [m for m in messages if m["role"] in ["user", "assistant", "system"]]
    system_prompt = load_system_prompt(page)
    full_messages = [{"role": "system", "content": system_prompt}] + filtered

    if count_tokens(full_messages) > TOKEN_THRESHOLD:
        summary_message = summarize_messages(messages)[0]
        recent = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
        full_messages = [summary_message] + recent
        messages = [summary_message] + recent

    # Add The One Ring reference text if user is on that page
    if page == "the-one-ring" and the_one_ring_texts:
        parts = []
        total = 0
        trimmed = False
        for name in sorted(the_one_ring_texts):
            text = the_one_ring_texts[name]
            if total >= 5000:
                trimmed = True
                break
            remaining = 5000 - total
            if len(text) > remaining:
                parts.append(text[:remaining])
                total += remaining
                trimmed = True
                break
            parts.append(text)
            total += len(text)

        if trimmed:
            print("Warning: Trimming The One Ring reference text due to size limit")

        reference = "\n\n".join(parts)
        full_messages.append(
            {
                "role": "system",
                "content": (
                    "The following text from 'The One Ring' is provided for your reference. "
                    "Do not reveal or quote it unless the user asks explicitly:\n" + reference
                ),
            }
        )

    if page == "the-one-ring" and the_one_ring_embeddings:
        try:
            # Get embedding of the current user message
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated:", bool(user_embedding))

            num_chunks = len(the_one_ring_embeddings)
            print(f"[DEBUG] Checked {num_chunks} text chunks for similarity.")

            # Find most similar chunk
            best = max(
                the_one_ring_embeddings,
                key=lambda x: cosine_similarity(user_embedding, x["embedding"]),
            )
            best_text = best["text"]
            best_source = best["source"]
            best_score = cosine_similarity(user_embedding, best["embedding"])
            print(
                f"[DEBUG] Best match from '{best_source}' with similarity score: {best_score:.4f}"
            )

            # Inject it into the system prompt
            full_messages.append(
                {
                    "role": "system",
                    "content": (
                        f"The following excerpt from '{best_source}' may be relevant. "
                        f"Do not reveal it unless the user explicitly asks:\n{best_text}"
                    ),
                }
            )
        except Exception as e:
            print("Embedding search failed:", e)

    response = client.chat.completions.create(
        model="gpt-4o", messages=full_messages, max_tokens=4096
    )
    trimmed = response.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": trimmed, "timestamp": timestamp})
    save_messages_to_file(messages)

    return jsonify({"response": trimmed})


if __name__ == "__main__":
    app.run(debug=True)
