"""
Enhanced chat history management for per-user, per-TTRPG persistence
"""
import os
import json
import datetime
from pathlib import Path


def get_user_history_dir(username):
    """Get the directory for a user's chat histories"""
    user_dir = Path("chat_histories") / username
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_history_filename(username, ttrpg_system="general"):
    """Get the filename for a specific user and TTRPG system"""
    user_dir = get_user_history_dir(username)
    return user_dir / f"{ttrpg_system}_chat.json"


def save_user_messages(messages, username, ttrpg_system="general"):
    """Save messages for a specific user and TTRPG system"""
    # Inject timestamp into any message that doesn't already have one
    for message in messages:
        if "timestamp" not in message:
            message["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add metadata about the session
    chat_data = {
        "username": username,
        "ttrpg_system": ttrpg_system,
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message_count": len(messages),
        "messages": messages
    }
    
    filename = get_history_filename(username, ttrpg_system)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)


def load_user_messages(username, ttrpg_system="general"):
    """Load messages for a specific user and TTRPG system"""
    filename = get_history_filename(username, ttrpg_system)
    
    if filename.exists():
        try:
            with open(filename, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            
            # Handle both old format (just messages) and new format (with metadata)
            if isinstance(chat_data, list):
                return chat_data  # Old format
            else:
                return chat_data.get("messages", [])  # New format
        except (json.JSONDecodeError, KeyError):
            print(f"Warning: Could not load chat history from {filename}")
            return []
    
    return []


def get_user_chat_sessions(username):
    """Get all available chat sessions for a user"""
    user_dir = get_user_history_dir(username)
    sessions = []
    
    for chat_file in user_dir.glob("*_chat.json"):
        ttrpg_system = chat_file.stem.replace("_chat", "")
        
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            
            # Handle both old and new formats
            if isinstance(chat_data, list):
                message_count = len(chat_data)
                last_updated = "Unknown"
            else:
                message_count = chat_data.get("message_count", 0)
                last_updated = chat_data.get("last_updated", "Unknown")
            
            sessions.append({
                "ttrpg_system": ttrpg_system,
                "message_count": message_count,
                "last_updated": last_updated,
                "filename": str(chat_file)
            })
        except (json.JSONDecodeError, KeyError):
            continue
    
    return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)


def archive_old_chats(username, keep_days=30):
    """Archive chat histories older than specified days"""
    user_dir = get_user_history_dir(username)
    archive_dir = user_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
    archived_count = 0
    
    for chat_file in user_dir.glob("*_chat.json"):
        if chat_file.stat().st_mtime < cutoff_date.timestamp():
            archive_file = archive_dir / chat_file.name
            chat_file.rename(archive_file)
            archived_count += 1
    
    return archived_count


# Backward compatibility functions
def save_messages_to_file(messages, filename="chat_history.json"):
    """Legacy function for backward compatibility"""
    for message in messages:
        if "timestamp" not in message:
            message["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def load_messages_from_file(filename="chat_history.json"):
    """Legacy function for backward compatibility"""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
