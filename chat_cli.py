import os
import datetime
import re
import json
from openai import OpenAI
from dotenv import load_dotenv
from token_counter import count_tokens
from message_history import load_messages_from_file, save_messages_to_file
from chapter_log import append_chapter_entry

# Load environment variables
load_dotenv()
client = OpenAI()

TOKEN_THRESHOLD = 150  # Low for testing

def summarize_messages(messages):
    to_summarize = [m for m in messages if m["role"] in ["user", "assistant"]]
    to_summarize = to_summarize[-12:]  # Last 12 messages for brevity

    summary_prompt = [
        {"role": "system", "content": "Summarize the following RPG conversation so far in a concise but detailed paragraph. Focus on world events, decisions made, and NPC interactions. Be specific."},
        *to_summarize
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=summary_prompt
    )

    summary = response.choices[0].message.content.strip()
    print("\n📘 Summary created and inserted into context.")
    return [{"role": "system", "content": f"SUMMARY OF EARLIER CHAT: {summary}"}]

def chat_loop():
    """Run the interactive chat session."""
    # Load system prompt
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    # Load previous messages
    messages = load_messages_from_file()

    while True:
        user_input = input("You: ").strip()

        # Exit condition
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting chat.")
            break

        # Chapter logging
        if user_input.startswith("#chapter"):
            try:
                _, rest = user_input.split(" ", 1)
                title, description = rest.split("|", 1)
                title = title.strip()
                description = description.strip()
                append_chapter_entry(title, description)
                messages.append({
                    "role": "chapter",
                    "content": f"#chapter {title} | {description}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                print(f"\n📖 Chapter logged: {title} — {description}")
            except ValueError:
                print("\n❌ Invalid format. Use: #chapter Chapter Title | Description")
            continue

        # Add user input
        messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Filter messages
        filtered_messages = [m for m in messages if m["role"] in ["user", "assistant", "system"]]
        full_messages = [{"role": "system", "content": system_prompt}] + filtered_messages

        # Token count
        token_count = count_tokens(full_messages)
        print(f"\n🔢 Total tokens used in request: {token_count}")

        # Summarization if threshold exceeded
        if token_count > TOKEN_THRESHOLD:
            summary_message = summarize_messages(messages)[0]
            recent = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
            full_messages = [summary_message] + recent
            messages = [summary_message] + recent
            print(f"\n📘 Injected summarization into system prompt.")

        # GPT response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=full_messages
        )

        # Extract and trim to 5 sentences
        reply = response.choices[0].message.content.strip()
        sentences = re.split(r'(?<=[.!?]) +', reply)
        trimmed_sentences = sentences[:5]

        # 🚨 ULTRA-HARD GUARDRAIL 🚨
        assert len(trimmed_sentences) <= 5, "GPT exceeded 5 sentence limit. Crashing as punishment."
    
        reply = ' '.join(trimmed_sentences).strip()

        print(f"\nGPT: {reply}\n")

        # Save assistant reply
        messages.append({
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        save_messages_to_file(messages)


if __name__ == "__main__":
    chat_loop()
