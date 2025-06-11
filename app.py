from flask_cors import CORS
from flask import Flask, request, jsonify
import datetime
import re
import os
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

# Load environment variables (e.g., API keys) from .env file and initialize OpenAI client
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

    filtered_messages = [m for m in messages if m["role"] in ["user", "assistant", "system"]]
    full_messages = [{"role": "system", "content": system_prompt}] + filtered_messages

    token_count = count_tokens(full_messages)
    if token_count > TOKEN_THRESHOLD:
        summary_message = summarize_messages(messages)[0]
        recent = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
        full_messages = [summary_message] + recent
        messages = [summary_message] + recent

    # Sends current conversation (with system prompt or summary) to OpenAI and extracts the reply.
    # Limits output to approx. 5 sentences (~100 tokens).
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=full_messages,
        max_tokens=100
    )

    trimmed = response.choices[0].message.content.strip()

    # Appends the AI’s trimmed reply to the message history with a timestamp.
    # Saves updated message history to disk via save_messages_to_file().
    messages.append({"role": "assistant", "content": trimmed, "timestamp": timestamp})
    save_messages_to_file(messages)

    # Returns the reply.
    return jsonify({"response": trimmed})


# Runs the App
if __name__ == "__main__":
    app.run(debug=True)
