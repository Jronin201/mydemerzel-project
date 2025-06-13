import os
import json
import datetime


def save_messages_to_file(messages, filename="chat_history.json"):
    # Inject timestamp into any message that doesn't already have one
    for message in messages:
        if "timestamp" not in message:
            message["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def load_messages_from_file(filename="chat_history.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
