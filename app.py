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

# Load env vars and system prompt
load_dotenv()
client = OpenAI()

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

    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=full_messages)
    reply = response.choices[0].message.content.strip()
    sentences = re.split(r'(?<=[.!?]) +', reply)
    trimmed = ' '.join(sentences[:5]).strip()

    assert len(sentences[:5]) <= 5, "GPT exceeded 5 sentence limit."

    messages.append({"role": "assistant", "content": trimmed, "timestamp": timestamp})
    save_messages_to_file(messages)

    return jsonify({"response": trimmed})

if __name__ == "__main__":
    app.run(debug=True)
