from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
import datetime
import re
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from token_counter import count_tokens
from message_history import load_messages_from_file, save_messages_to_file
from chapter_log import append_chapter_entry

app = Flask(__name__, static_folder='static')
# Explicitly allow cross-origin requests from any domain to fix frontend CORS errors
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/the-one-ring')
def the_one_ring():
    return app.send_static_file('the-one-ring/index.html')

@app.route('/call-of-cthulhu')
def call_of_cthulhu():
    return app.send_static_file('call-of-cthulhu/index.html')

@app.route('/master-template')
def master_template():
    return app.send_static_file('master-template/index.html')

# Load environment variables and OpenAI client
load_dotenv()
client = OpenAI()

# Load system prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()

TOKEN_THRESHOLD = 150
messages = load_messages_from_file()


def summarize_messages(messages):
    to_summarize = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
    summary_prompt = [{"role": "system", "content": "Summarize the following RPG conversation so far in a concise but detailed paragraph. Focus on world events, decisions made, and NPC interactions. Be specific."}] + to_summarize
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=summary_prompt)
    summary = response.choices[0].message.content.strip()
    return [{"role": "system", "content": f"SUMMARY OF EARLIER CHAT: {summary}"}]

@app.route("/chat", methods=["POST"])
@cross_origin()       # explicitly allow all origins
def chat():
    global messages
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages.append({"role": "user", "content": user_input, "timestamp": timestamp})

    if user_input == "?":
        help_text = "**Available Commands:**\n- `?` – Show this help menu"
        messages.append({"role": "assistant", "content": help_text, "timestamp": timestamp})
        save_messages_to_file(messages)
        return jsonify({"response": help_text})

    filtered = [m for m in messages if m["role"] in ["user", "assistant", "system"]]
    full_messages = [{"role": "system", "content": system_prompt}] + filtered

    if count_tokens(full_messages) > TOKEN_THRESHOLD:
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

if __name__ == "__main__":
    app.run(debug=True)
