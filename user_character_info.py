"""
Character information persistence for per-user, per-TTRPG storage
Stores Character Information and Notes textbox content persistently with change history
"""
import os
import json
import datetime
from pathlib import Path


def get_user_character_dir(username):
    """Get the directory for a user's character information"""
    user_dir = Path("character_info") / username
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_character_info_filename(username, ttrpg_system="general"):
    """Get the filename for a specific user and TTRPG system's character info"""
    user_dir = get_user_character_dir(username)
    return user_dir / f"{ttrpg_system}_character.json"


def save_user_character_info(username, ttrpg_system="general", character_name="", character_stats="", source="user"):
    """Save character information for a specific user and TTRPG system with history tracking"""
    filename = get_character_info_filename(username, ttrpg_system)
    
    # Load existing data to preserve history
    existing_data = {}
    if filename.exists():
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, KeyError):
            existing_data = {}
    
    # Get current values for history
    current_info = existing_data.get("character_info", {})
    current_name = current_info.get("name", "")
    current_stats = current_info.get("stats", "")
    
    # Only save to history if there's actually a change
    if current_name != character_name or current_stats != character_stats:
        # Initialize history if it doesn't exist
        if "history" not in existing_data:
            existing_data["history"] = []
        
        # Add current state to history before updating
        if current_name or current_stats:  # Only add to history if there was previous content
            history_entry = {
                "character_info": {
                    "name": current_name,
                    "stats": current_stats
                },
                "timestamp": existing_data.get("last_updated", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "source": existing_data.get("last_source", "user")
            }
            existing_data["history"].append(history_entry)
            
            # Keep only last 50 changes to prevent file from growing too large
            if len(existing_data["history"]) > 50:
                existing_data["history"] = existing_data["history"][-50:]
    
    # Update with new data
    character_data = {
        "username": username,
        "ttrpg_system": ttrpg_system,
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_source": source,  # Track whether change was from "user" or "ai"
        "character_info": {
            "name": character_name,
            "stats": character_stats
        },
        "history": existing_data.get("history", [])
    }
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving character info: {e}")
        return False


def load_user_character_info(username, ttrpg_system="general"):
    """Load character information for a specific user and TTRPG system"""
    filename = get_character_info_filename(username, ttrpg_system)
    
    if filename.exists():
        try:
            with open(filename, "r", encoding="utf-8") as f:
                character_data = json.load(f)
            
            # Return character info or defaults
            character_info = character_data.get("character_info", {})
            return {
                "character_name": character_info.get("name", ""),
                "character_stats": character_info.get("stats", ""),
                "last_updated": character_data.get("last_updated", "Never")
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load character info from {filename}: {e}")
            return {"character_name": "", "character_stats": "", "last_updated": "Never"}
    
    return {"character_name": "", "character_stats": "", "last_updated": "Never"}


def undo_character_info_change(username, ttrpg_system="general"):
    """Undo the most recent change to character information"""
    filename = get_character_info_filename(username, ttrpg_system)
    
    if not filename.exists():
        return {"success": False, "message": "No character information found to undo"}
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            character_data = json.load(f)
        
        history = character_data.get("history", [])
        
        if not history:
            return {"success": False, "message": "No changes to undo"}
        
        # Get the most recent history entry (the previous state)
        previous_state = history.pop()  # Remove and get the last entry
        
        # Restore the previous state
        character_data["character_info"] = previous_state["character_info"]
        character_data["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        character_data["last_source"] = "undo"
        character_data["history"] = history  # Save the history without the restored entry
        
        # Save the updated data
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Successfully undid the last change",
            "character_name": character_data["character_info"]["name"],
            "character_stats": character_data["character_info"]["stats"],
            "restored_from": previous_state["timestamp"]
        }
        
    except Exception as e:
        print(f"Error undoing character info change: {e}")
        return {"success": False, "message": f"Error undoing change: {e}"}


def get_character_info_history(username, ttrpg_system="general", limit=10):
    """Get the change history for character information"""
    filename = get_character_info_filename(username, ttrpg_system)
    
    if not filename.exists():
        return []
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            character_data = json.load(f)
        
        history = character_data.get("history", [])
        
        # Return the most recent changes (up to limit)
        return history[-limit:] if len(history) > limit else history
        
    except Exception as e:
        print(f"Error loading character info history: {e}")
        return []


# Updated function signature to include source parameter for backwards compatibility
def get_user_character_sessions(username):
    """Get all available character info sessions for a user"""
    user_dir = get_user_character_dir(username)
    sessions = []
    
    if not user_dir.exists():
        return sessions
    
    for character_file in user_dir.glob("*_character.json"):
        ttrpg_system = character_file.stem.replace("_character", "")
        
        try:
            with open(character_file, "r", encoding="utf-8") as f:
                character_data = json.load(f)
            
            character_info = character_data.get("character_info", {})
            last_updated = character_data.get("last_updated", "Unknown")
            
            sessions.append({
                "ttrpg_system": ttrpg_system,
                "character_name": character_info.get("name", ""),
                "character_stats": character_info.get("stats", ""),
                "last_updated": last_updated,
                "filename": str(character_file)
            })
        except (json.JSONDecodeError, KeyError):
            continue
    
    return sorted(sessions, key=lambda x: x["last_updated"], reverse=True)


def archive_old_character_info(username, keep_days=90):
    """Archive character info older than specified days"""
    user_dir = get_user_character_dir(username)
    archive_dir = user_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
    archived_count = 0
    
    for character_file in user_dir.glob("*_character.json"):
        if character_file.stat().st_mtime < cutoff_date.timestamp():
            archive_file = archive_dir / character_file.name
            character_file.rename(archive_file)
            archived_count += 1
    
    return archived_count


def delete_user_character_info(username, ttrpg_system="general"):
    """Delete character information for a specific user and TTRPG system"""
    filename = get_character_info_filename(username, ttrpg_system)
    
    if filename.exists():
        try:
            filename.unlink()
            return True
        except Exception as e:
            print(f"Error deleting character info: {e}")
            return False
    
    return True  # Already doesn't exist


# Utility function for getting all character info for a user
def get_all_user_character_info(username):
    """Get character information for all TTRPG systems for a user"""
    sessions = get_user_character_sessions(username)
    character_info_dict = {}
    
    for session in sessions:
        character_info_dict[session["ttrpg_system"]] = {
            "character_name": session["character_name"],
            "character_stats": session["character_stats"],
            "last_updated": session["last_updated"]
        }
    
    return character_info_dict
