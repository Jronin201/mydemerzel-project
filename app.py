from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from flask_login import (
    LoginManager, login_user, login_required, logout_user, UserMixin, current_user
)
import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
from token_counter import count_tokens
from message_history import load_messages_from_file, save_messages_to_file
import numpy as np
from pathlib import Path
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "scripts"))

try:
    from chatbot_campaign_manager import process_user_request
except ImportError:
    def process_user_request(user_request, session_state=None):
        print(f"[STUB] process_user_request called with: {user_request}")
        return {"response": "Campaign manager not available.", "takeover": False, "session_state": session_state or {}}

app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/*": {"origins": "*"}})

# --- FIX: Use a secure secret key from environment variable ---
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "REPLACE_WITH_A_SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # type: ignore[attr-defined]


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "Demerzel" and password == "Seraphine":
            user = User(id="Demerzel")
            login_user(user)
            return redirect(url_for("root"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def root():
    return app.send_static_file("index.html")


# --- FIX: Load embeddings and reference texts globally for all routes ---
the_one_ring_embeddings = []
if Path("embeddings/the-one-ring.json").exists():
    with open("embeddings/the-one-ring.json", "r", encoding="utf-8") as f:
        the_one_ring_embeddings = json.load(f)
the_one_ring_texts = {}
tor_dir = os.path.join(app.static_folder or "static", "text", "the-one-ring")
if os.path.isdir(tor_dir):
    for fname in os.listdir(tor_dir):
        if fname.endswith(".txt"):
            with open(os.path.join(tor_dir, fname), "r", encoding="utf-8") as f:
                the_one_ring_texts[fname] = f.read()

dune_embeddings = []
if Path("embeddings/dune.json").exists():
    with open("embeddings/dune.json", "r", encoding="utf-8") as f:
        dune_embeddings = json.load(f)


@app.route("/the-one-ring")
@login_required
def the_one_ring():
    return app.send_static_file("the-one-ring/index.html")


@app.route("/dune")
@login_required
def dune():
    system_prompt = load_system_prompt("dune")
    return app.send_static_file("dune/index.html")

from flask import request, jsonify

@app.route("/call-of-cthulhu")
@login_required
def call_of_cthulhu():
    return app.send_static_file("call-of-cthulhu/index.html")


@app.route("/master-template")
@login_required
def master_template():
    return app.send_static_file("master-template/index.html")


# --- Example endpoints for campaign creation and compliance ---
# FIX: Provide stubs for undefined functions so code runs
def create_campaign():
    # Placeholder implementation
    return {"campaign": "example campaign"}

def check_compliance(scenario, rules_file_path, threshold):
    # Placeholder implementation
    return True, []

@app.route('/create_campaign', methods=['POST'])
def create_campaign_endpoint():
    scenario = create_campaign()
    return jsonify(scenario)


@app.route('/compliance_check', methods=['POST'])
def compliance_check_endpoint():
    data = request.json
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    scenario = data.get('scenario', {})
    rules_file_path = data.get('rules_file_path', '')
    threshold = data.get('threshold', 0.5)
    compliant, corrections = check_compliance(scenario, rules_file_path, threshold)
    return jsonify({"compliant": compliant, "corrections": corrections})


@app.route('/process_request', methods=['POST'])
def process_request_endpoint():
    data = request.json
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    user_request = data.get('user_request', '')
    process_user_request(user_request)
    return jsonify({"status": "Processed"})


# --- Load environment variables and OpenAI client ---
load_dotenv()
client = OpenAI()

from pathlib import Path

def load_system_prompt(page: str) -> str:
    """Load global prompt first, then append any page-specific prompt.
    For 'dune' page, also append the dune_campaign.txt content."""
    base_prompt_path = Path("system_prompt.txt")
    base_prompt = base_prompt_path.read_text(encoding="utf-8").strip() if base_prompt_path.exists() else ""
    
    page_prompt = ""
    if page:
        page_path = Path("static") / page / "system_prompt.txt"
        if page_path.exists():
            page_prompt = page_path.read_text(encoding="utf-8").strip()
    
    campaign_prompt = ""
    if page == "dune":
        campaign_path = Path("dune_campaign.txt")
        if campaign_path.exists():
            campaign_prompt = campaign_path.read_text(encoding="utf-8").strip()
    
    # Combine all prompts
    combined_prompt = "\n\n".join(filter(None, [base_prompt, page_prompt, campaign_prompt]))
    return combined_prompt

TOKEN_THRESHOLD = 12000

# --- FIX: Store messages per session/user in production; for now, keep global for demo ---
messages = load_messages_from_file()


def summarize_messages(messages):
    # Use OpenAI message classes for message objects to match expected types
    from openai.types.chat import (
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
    )

    to_summarize = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
    summary_prompt: list = [
        ChatCompletionSystemMessageParam(
            role="system",
            content="Summarize the following RPG conversation so far in a concise but detailed paragraph. Focus on world events, decisions made, and NPC interactions. Be specific.",
        )
    ]
    for m in to_summarize:
        if m["role"] == "user":
            summary_prompt.append(ChatCompletionUserMessageParam(role="user", content=m["content"]))
        elif m["role"] == "assistant":
            summary_prompt.append(ChatCompletionAssistantMessageParam(role="assistant", content=m["content"]))

    response = client.chat.completions.create(
        model="gpt-4o", messages=summary_prompt
    )
    content = response.choices[0].message.content
    summary = content.strip() if content is not None else ""
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
        for candidate in ["the-one-ring", "dune", "call-of-cthulhu", "master-template"]:
            if candidate in ref:
                page = candidate
                break
    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    # ---------- AGENT TAKEOVER FOR DUNE ----------
    if page == "dune":
        session_state = session.get("campaign_state", None)
        result = process_user_request(user_input, session_state)
        session["campaign_state"] = result.get("session_state", {})

        if result.get("takeover", False):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
            messages.append({"role": "assistant", "content": result["response"], "timestamp": timestamp})
            save_messages_to_file(messages)
            return jsonify({"response": result["response"]})

        if result.get("response") and not result.get("takeover"):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
            messages.append({"role": "assistant", "content": result["response"], "timestamp": timestamp})
            save_messages_to_file(messages)
            return jsonify({"response": result["response"]})
    # -------- END AGENT TAKEOVER SECTION --------


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
    full_system_prompt = system_prompt

    full_messages_preview = [{"role": "system", "content": full_system_prompt}] + filtered
    if count_tokens(full_messages_preview) > TOKEN_THRESHOLD:
        summary_message = summarize_messages(messages)[0]
        recent = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
        filtered = [summary_message] + recent
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
        full_system_prompt += (
            "\n\n[REFERENCE TEXT FROM 'The One Ring']\n"
            "Do not reveal or quote this unless the user explicitly asks:\n" + reference
        )

    if page == "the-one-ring" and the_one_ring_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated:", bool(user_embedding))

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

            full_system_prompt += (
                f"\n\n[RELEVANT EXCERPT FROM '{best_source}']\n"
                f"Do not reveal this unless the user explicitly asks:\n{best_text}"
            )
        except Exception as e:
            print("Embedding search failed:", e)

    if page == "dune" and dune_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated for Dune:", bool(user_embedding))

            best = max(
                dune_embeddings,
                key=lambda x: cosine_similarity(user_embedding, x["embedding"]),
            )
            best_text = best["text"]
            best_source = best["source"]
            best_score = cosine_similarity(user_embedding, best["embedding"])
            print(
                f"[DEBUG] Best Dune match from '{best_source}' with similarity score: {best_score:.4f}"
            )

            full_system_prompt += (
                f"\n\n[RELEVANT EXCERPT FROM '{best_source}']\n"
                f"Do not reveal this unless the user explicitly asks:\n{best_text}"
            )
        except Exception as e:
            print("Dune embedding search failed:", e)

    from openai.types.chat import (
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
        ChatCompletionAssistantMessageParam,
    )

    def dict_to_message_param(msg):
        if msg["role"] == "system":
            return ChatCompletionSystemMessageParam(role="system", content=msg["content"])
        elif msg["role"] == "user":
            return ChatCompletionUserMessageParam(role="user", content=msg["content"])
        elif msg["role"] == "assistant":
            return ChatCompletionAssistantMessageParam(role="assistant", content=msg["content"])
        else:
            raise ValueError(f"Unknown role: {msg['role']}")

    full_messages_dicts = [{"role": "system", "content": full_system_prompt}] + filtered
    full_messages = [dict_to_message_param(m) for m in full_messages_dicts]

    response = client.chat.completions.create(
        model="gpt-4o", messages=full_messages, max_tokens=4096
    )
    content = response.choices[0].message.content
    trimmed = content.strip() if content is not None else ""
    messages.append({"role": "assistant", "content": trimmed, "timestamp": timestamp})
    save_messages_to_file(messages)

    return jsonify({"response": trimmed})


if __name__ == "__main__":
    app.run(debug=True)
