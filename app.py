from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
import datetime
import re
import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from token_counter import count_tokens
from message_history import load_messages_from_file, save_messages_to_file
from chapter_log import append_chapter_entry

app = Flask(__name__)
CORS(app)

# Load environment variables (e.g., API keys) from .env file and initialize OpenAI client
load_dotenv()
client = OpenAI()

# Load system prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()

# Set a token threshold for summarization. If total tokens exceed this, older messages will be summarized.
TOKEN_THRESHOLD = 150
messages = load_messages_from_file()

# Takes the last 12 user/assistant messages and sends them to OpenAI with a prompt to summarize.
# Returns a new system message containing the summary, used to compress old context.
def summarize_messages(messages):
    to_summarize = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
    summary_prompt = [{"role": "system", "content": "Summarize the following RPG conversation so far in a concise but detailed paragraph. Focus on world events, decisions made, and NPC interactions. Be specific."}] + to_summarize
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=summary_prompt)
    summary = response.choices[0].message.content.strip()
    return [{"role": "system", "content": f"SUMMARY OF EARLIER CHAT: {summary}"}]

# Listens for POST requests from frontend.
@app.route("/chat", methods=["POST"])
def chat():
    global messages
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages.append({"role": "user", "content": user_input, "timestamp": timestamp})

    # 🔹 Check for help command
    if user_input == "?":
        help_text = (
            "**Available Commands:**\n"
            "- `save [name]` – Saves the current character sheet to the server\n"
            "- `load [name]` – Loads the specified character sheet\n"
            "- `show [elf|dwarf|hobbit|man]` – Displays one of the sample character sheets\n"
            "- `hide` or `remove` – Hides the currently displayed sheet\n"
            "- `?` – Show this help menu\n"
        )
        messages.append({"role": "assistant", "content": help_text, "timestamp": timestamp})
        save_messages_to_file(messages)
        return jsonify({"response": help_text})

    filtered_messages = [m for m in messages if m["role"] in ["user", "assistant", "system"]]
    full_messages = [{"role": "system", "content": system_prompt}] + filtered_messages

    token_count = count_tokens(full_messages)
    if token_count > TOKEN_THRESHOLD:
        summary_message = summarize_messages(messages)[0]
        recent = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
        full_messages = [summary_message] + recent
        messages = [summary_message] + recent

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=full_messages,
        max_tokens=100
    )

    trimmed = response.choices[0].message.content.strip()

    messages.append({"role": "assistant", "content": trimmed, "timestamp": timestamp})
    save_messages_to_file(messages)

    return jsonify({"response": trimmed})

# Normalize character names for consistent filename formatting
def normalize_filename(name):
    name = name.lower().strip().rstrip(".")
    name = re.sub(r"[^\w\s-]", "", name)
    return name.replace(" ", "_")

# Save uploaded base64 PDF to disk
@app.route('/save-character', methods=['POST'])
def save_character():
    data = request.json
    name = data.get('name')
    pdf_data = data.get('pdfData')

    if not name or not pdf_data:
        return jsonify({'error': 'Missing name or pdfData'}), 400

    filename = f"/mnt/data/{normalize_filename(name)}.pdf"
    try:
        with open(filename, "wb") as f:
            f.write(base64.b64decode(pdf_data))
        return jsonify({'message': f'Character sheet saved as {name}.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Load saved PDF by name
@app.route('/load-character/<name>', methods=['GET'])
def load_character(name):
    filename = f"/mnt/data/{normalize_filename(name)}.pdf"
    if not os.path.exists(filename):
        return jsonify({'error': 'Character not found'}), 404
    return send_file(filename, mimetype='application/pdf')

# Runs the App
if __name__ == "__main__":
    app.run(debug=True)
