import os
import json
from datetime import datetime

CHAPTER_LOG_FILE = "chapter_log.json"

def load_chapter_log():
    if os.path.exists(CHAPTER_LOG_FILE):
        with open(CHAPTER_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chapter_log(log):
    with open(CHAPTER_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def append_chapter_entry(title, description):
    log = load_chapter_log()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.append({
        "timestamp": timestamp,
        "title": title,
        "description": description
    })
    save_chapter_log(log)
