import os
import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Optional: Set up Git configuration for deployment environments only
if os.environ.get("DEPLOYMENT_ENV") == "render":
    import subprocess
    # Only configure Git in deployment environments, not development
    subprocess.run(
        ["git", "config", "user.email", "render-bot@yourdomain.com"],
        check=False
    )
    subprocess.run(
        ["git", "config", "user.name", "Render Bot"],
        check=False
    )
    
    # Set up GitHub token for deployments
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        repo = "github.com/Jronin201/mydemerzel-project.git"
        subprocess.run(
            ["git", "remote", "set-url", "origin", f"https://{token}@{repo}"],
            check=False
        )

from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from flask_login import (
    LoginManager, login_user, login_required, logout_user, UserMixin, current_user
)
import datetime
from openai import OpenAI
try:
    # Newer SDK exceptions
    from openai import APIStatusError, APIConnectionError, RateLimitError, AuthenticationError, BadRequestError, APITimeoutError
except Exception:  # pragma: no cover
    APIStatusError = APIConnectionError = RateLimitError = AuthenticationError = BadRequestError = APITimeoutError = Exception
from token_counter import count_tokens
from message_history import load_messages_from_file, save_messages_to_file
from user_chat_history import save_user_messages, load_user_messages, get_user_chat_sessions
from user_character_info import save_user_character_info, load_user_character_info, get_user_character_sessions, undo_character_info_change, get_character_info_history
from memory_optimized_search import memory_optimized_embedding_search, get_best_matches_across_systems
from memory_optimized_embeddings import get_system_embeddings, get_embedding_status, clear_embedding_cache
import numpy as np
from pathlib import Path
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "scripts"))
import random

try:
    from chatbot_campaign_manager import process_user_request
except ImportError:
    def process_user_request(user_request, session_state=None, character_name=None, character_stats=None):
        print(f"[STUB] process_user_request called with: {user_request}")
        return {"response": "Campaign manager not available.", "takeover": False, "session_state": session_state or {}}

app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/*": {"origins": "*"}})

# Security headers middleware
@app.after_request
def after_request(response):
    # Security headers for better browser compatibility and security
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # CSP header for locked-down environments
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'"
    )
    response.headers['Content-Security-Policy'] = csp
    
    return response

# --- FIX: Use a secure secret key from environment variable ---
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "REPLACE_WITH_A_SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # type: ignore[attr-defined]

# Error handlers for better user experience
@app.errorhandler(404)
def not_found_error(error):
    return render_template('login.html', error="Page not found. Please login to continue."), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error. Please try again later."}), 500

@app.errorhandler(502)
def bad_gateway_error(error):
    return jsonify({"error": "Service temporarily unavailable. Please try again in a moment."}), 502

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('login.html', error="Access forbidden. Please login."), 403


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


# --- Enhanced Lockdown Embedding Loading with Memory Optimization ---
print("🔧 Initializing TTRPG embedding systems for lockdown environment...")

# Try to import the lockdown embedding loader for seamless deployment
try:
    # Debug environment variables for Render deployment
    print("🔍 Environment Variables Debug:")
    print(f"   SUPABASE_PROJECT_URL: {os.getenv('SUPABASE_PROJECT_URL', 'NOT SET')}")
    print(f"   SUPABASE_ANON_KEY: {'SET' if os.getenv('SUPABASE_ANON_KEY') else 'NOT SET'}")
    print(f"   SUPABASE_BUCKET_NAME: {os.getenv('SUPABASE_BUCKET_NAME', 'NOT SET')}")
    
    from lockdown_embedding_loader import download_embeddings_if_missing
    print("📦 Using lockdown embedding loader for Supabase downloads")
    
    # Force download to ensure files are available
    download_success = download_embeddings_if_missing()
    if download_success:
        print("✅ Supabase embeddings downloaded successfully")
    else:
        print("⚠️  Supabase download failed - will try to continue with existing files")
        
except ImportError as e:
    print(f"📦 ImportError with lockdown loader: {e}")
    print("📦 Continuing without automatic download capability")
except Exception as e:
    print(f"❌ Error during embedding download: {e}")
    print("📦 Continuing with any existing embedding files")
    import traceback
    print(f"   Traceback: {traceback.format_exc()}")

# Update memory-optimized manager to match actual Supabase file names
from memory_optimized_embeddings import embedding_manager
embedding_manager.embedding_files = {
    'dune': {
        'optimized': 'embeddings/dune.json',  # Match Supabase names
        'fallback': 'embeddings/dune_optimized.json'  # Reverse priority if both exist
    },
    'the-one-ring': {
        'optimized': 'embeddings/the-one-ring.json',  # Match Supabase names
        'fallback': 'embeddings/the-one-ring_optimized.json'
    },
    'mouse-guard': {
        'optimized': 'embeddings/mouse-guard.json',  # Match Supabase names
        'fallback': 'embeddings/mouse-guard_optimized.json'
    },
    'pendragon': {
        'optimized': 'embeddings/pendragon.json',  # Future embedding file
        'fallback': 'embeddings/pendragon_optimized.json'
    }
}

print("✅ Memory-optimized embedding system ready with Supabase integration")
print("📊 Embedding files will be loaded on demand from:")

# Check what embedding files exist after download attempt
for system_name, files in embedding_manager.embedding_files.items():
    optimized_path = Path(files['optimized'])
    if optimized_path.exists():
        size_mb = optimized_path.stat().st_size / (1024 * 1024)
        print(f"   {system_name}: {size_mb:.1f}MB (available)")
    else:
        print(f"   {system_name}: Not available")

# Note: Embeddings are now loaded only when a specific TTRPG system is accessed
# This prevents memory exhaustion during startup

# Load The One Ring reference texts
the_one_ring_texts = {}
tor_dir = os.path.join(app.static_folder or "static", "text", "the-one-ring")
if os.path.isdir(tor_dir):
    for fname in os.listdir(tor_dir):
        if fname.endswith(".txt"):
            with open(os.path.join(tor_dir, fname), "r", encoding="utf-8") as f:
                the_one_ring_texts[fname] = f.read()

# --- Enhanced TTRPG Configuration Management ---
def load_ttrpg_config():
    """Load the centralized TTRPG configuration."""
    config_path = Path("ttrpg-config.json")
    
    if not config_path.exists():
        # Return default config with existing systems
        return {
            "systems": {
                "dune": {
                    "display_name": "Dune: Adventures in the Imperium",
                    "description": "Political intrigue and survival in Frank Herbert's Dune universe",
                    "active": True,
                    "has_custom_page": False,
                    "has_embeddings": True,
                    "created_date": "2024-01-01",
                    "version": "1.0",
                    "game_master_title": "Game Master"
                },
                "the-one-ring": {
                    "display_name": "The One Ring",
                    "description": "Adventures in Tolkien's Middle-earth during the Third Age",
                    "active": True,
                    "has_custom_page": False,
                    "has_embeddings": True,
                    "created_date": "2024-01-01",
                    "version": "1.0",
                    "game_master_title": "Loremaster"
                },
                "call-of-cthulhu": {
                    "display_name": "Call of Cthulhu",
                    "description": "Cosmic horror investigations in the 1920s",
                    "active": True,
                    "has_custom_page": False,
                    "has_embeddings": False,
                    "created_date": "2024-01-01",
                    "version": "1.0",
                    "game_master_title": "Keeper"
                },
                "mouse-guard": {
                    "display_name": "Mouse Guard",
                    "description": "Brave mice defending their communities from natural dangers",
                    "active": True,
                    "has_custom_page": False,
                    "has_embeddings": True,
                    "created_date": "2024-01-01",
                    "version": "1.0",
                    "game_master_title": "Game Master"
                },
                "pendragon": {
                    "display_name": "Pendragon 6th Edition",
                    "description": "Arthurian knights in the legendary realm of King Arthur and the Round Table",
                    "active": True,
                    "has_custom_page": False,
                    "has_embeddings": False,
                    "created_date": "2025-07-21",
                    "version": "1.0",
                    "game_master_title": "Game Master"
                }
            },
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.datetime.now().isoformat(),
                "total_systems": 5,
                "active_systems": 5
            }
        }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Fallback to default if JSON is corrupted
        return load_ttrpg_config()

def get_available_ttrpgs():
    """Get list of available TTRPG systems."""
    config = load_ttrpg_config()
    return [name for name, system in config.get("systems", {}).items() 
            if system.get("active", True)]

def get_ttrpg_info(ttrpg_name):
    """Get information about a specific TTRPG."""
    config = load_ttrpg_config()
    return config.get("systems", {}).get(ttrpg_name, None)

def register_dynamic_routes():
    """Register routes for all active TTRPGs."""
    available_systems = get_available_ttrpgs()
    
    for ttrpg_name in available_systems:
        # Skip if route already exists
        if f"/{ttrpg_name}" in [rule.rule for rule in app.url_map.iter_rules()]:
            continue
            
        # Create redirect route for each TTRPG
        def make_route_handler(name):
            def route_handler():
                return redirect(url_for('ttrpg_chatbot') + f'?ttrpg={name}')
            return route_handler
        
        route_handler = make_route_handler(ttrpg_name)
        route_handler.__name__ = f'{ttrpg_name}_route'
        
        app.add_url_rule(f'/{ttrpg_name}', ttrpg_name, route_handler)

# --- TTRPG Management Functions ---
def load_current_ttrpg():
    """Load the current TTRPG configuration from file"""
    try:
        with open("current_ttrpg.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default configuration if file doesn't exist or is invalid
        return {
            "current_ttrpg": "general",
            "session_start": None,
            "last_updated": None,
            "character_info": {"name": "", "stats": ""},
            "available_systems": get_available_ttrpgs()
        }

def save_current_ttrpg(ttrpg_data):
    """Save the current TTRPG configuration to file"""
    try:
        with open("current_ttrpg.json", "w", encoding="utf-8") as f:
            json.dump(ttrpg_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving TTRPG data: {e}")
        return False

def update_current_ttrpg(ttrpg_name, character_name="", character_stats=""):
    """Update the current TTRPG and character information"""
    ttrpg_data = load_current_ttrpg()
    ttrpg_data["current_ttrpg"] = ttrpg_name
    ttrpg_data["last_updated"] = datetime.datetime.now().isoformat()
    if not ttrpg_data.get("session_start"):
        ttrpg_data["session_start"] = datetime.datetime.now().isoformat()
    
    # Update character info if provided
    if character_name or character_stats:
        ttrpg_data["character_info"]["name"] = character_name
        ttrpg_data["character_info"]["stats"] = character_stats
    
    save_current_ttrpg(ttrpg_data)
    return ttrpg_data

# --- Updated Routes ---
@app.route("/ttrpg-chatbot")
@login_required
def ttrpg_chatbot():
    """Universal TTRPG chatbot page"""
    # Get the TTRPG from URL parameter
    ttrpg = request.args.get('ttrpg', 'general')
    
    # Validate that the TTRPG exists and is active
    if ttrpg != 'general':
        available_systems = get_available_ttrpgs()
        if ttrpg not in available_systems:
            # If invalid TTRPG, redirect to general or first available
            if available_systems:
                return redirect(url_for('ttrpg_chatbot') + f'?ttrpg={available_systems[0]}')
            else:
                ttrpg = 'general'
    
    # Update the current TTRPG
    update_current_ttrpg(ttrpg)
    
    return app.send_static_file("ttrpg-chatbot/index.html")

# --- Keep old routes for backward compatibility (redirect to new universal page) ---
@app.route("/the-one-ring")
@login_required
def the_one_ring():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=the-one-ring')

@app.route("/dune")
@login_required
def dune():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=dune')

@app.route("/call-of-cthulhu")
@login_required
def call_of_cthulhu():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=call-of-cthulhu')

@app.route("/mouse-guard")
@login_required
def mouse_guard():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=mouse-guard')

@app.route("/pendragon")
@login_required
def pendragon():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=pendragon')

@app.route("/master-template")
@login_required
def master_template():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=master-template')

# --- API endpoints for TTRPG management ---
@app.route("/api/embedding-status", methods=["GET"])
@login_required 
def get_embedding_status():
    """Get current status of embedding files for diagnostics and user feedback"""
    try:
        # Use memory-optimized embedding status
        status = get_embedding_status()
        return jsonify(status)
    except Exception as e:
        print(f"❌ Error getting embedding status: {e}")
        # Fallback status 
        return jsonify({
            "optimization_active": True,
            "cache_status": {"cached_systems": [], "cache_size": 0},
            "memory_usage": {"estimated_memory_mb": 0},
            "file_status": {},
            "error": str(e)
        })

@app.route("/api/current-ttrpg", methods=["GET"])
@login_required
def get_current_ttrpg():
    """Get the current TTRPG configuration"""
    return jsonify(load_current_ttrpg())

@app.route("/api/current-ttrpg", methods=["POST"])
@login_required
def set_current_ttrpg():
    """Update the current TTRPG configuration"""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    ttrpg_name = data.get("ttrpg", "general")
    character_name = data.get("character_name", "")
    character_stats = data.get("character_stats", "")
    
    updated_data = update_current_ttrpg(ttrpg_name, character_name, character_stats)
    return jsonify(updated_data)

@app.route("/api/chat-history", methods=["GET"])
@login_required
def get_chat_history():
    """Get chat history for the current user and TTRPG system"""
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    ttrpg_system = request.args.get("ttrpg", "general")
    
    messages = get_user_messages(username, ttrpg_system)
    
    return jsonify({
        "username": username,
        "ttrpg_system": ttrpg_system,
        "message_count": len(messages),
        "messages": messages
    })

@app.route("/api/chat-history/undo", methods=["POST"])
@login_required
def undo_chat_step():
    """Step back in chat history by removing the last message (either user or assistant)"""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    ttrpg_system = data.get("ttrpg", "general")
    
    messages = get_user_messages(username, ttrpg_system)
    
    # Check if there are any messages to undo
    if len(messages) == 0:
        return jsonify({
            "success": False,
            "message": "No messages to undo",
            "undone_user_message": "",
            "remaining_count": 0
        })
    
    # Remove the last message, regardless of role
    undone_message = messages.pop()
    undone_user_message = undone_message.get("content", "") if undone_message.get("role") == "user" else ""
    
    # Save the updated chat history
    save_user_chat(messages, username, ttrpg_system)
    
    return jsonify({
        "success": True,
        "message": f"Undid last {undone_message.get('role', 'unknown')} message",
        "undone_user_message": undone_user_message,
        "remaining_count": len(messages)
    })

@app.route("/api/chat-sessions", methods=["GET"])
@login_required  
def get_chat_sessions():
    """Get all available chat sessions for the current user"""
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    sessions = get_user_chat_sessions(username)
    
    return jsonify({
        "username": username,
        "sessions": sessions
    })


@app.route("/api/character-info", methods=["GET"])
@login_required
def get_character_info():
    """Get character information for the current user and TTRPG system"""
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    ttrpg_system = request.args.get("ttrpg", "general")
    
    character_info = load_user_character_info(username, ttrpg_system)
    
    return jsonify({
        "username": username,
        "ttrpg_system": ttrpg_system,
        "character_name": character_info.get("character_name", ""),
        "character_stats": character_info.get("character_stats", ""),
        "last_updated": character_info.get("last_updated", "Never")
    })


@app.route("/api/character-info", methods=["POST"])
@login_required
def set_character_info():
    """Update character information for the current user and TTRPG system"""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    ttrpg_system = data.get("ttrpg", "general")
    character_name = data.get("character_name", "")
    character_stats = data.get("character_stats", "")
    source = data.get("source", "user")  # Default to user, can be "ai" for AI updates
    
    success = save_user_character_info(username, ttrpg_system, character_name, character_stats, source)
    
    if success:
        return jsonify({
            "success": True,
            "username": username,
            "ttrpg_system": ttrpg_system,
            "character_name": character_name,
            "character_stats": character_stats
        })
    else:
        return jsonify({"error": "Failed to save character information"}), 500


@app.route("/api/character-sessions", methods=["GET"])
@login_required
def get_character_sessions():
    """Get all available character info sessions for the current user"""
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    sessions = get_user_character_sessions(username)
    
    return jsonify({
        "username": username,
        "sessions": sessions
    })


@app.route("/api/character-info/undo", methods=["POST"])
@login_required
def undo_character_info():
    """Undo the most recent change to character information"""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    ttrpg_system = data.get("ttrpg", "general")
    
    result = undo_character_info_change(username, ttrpg_system)
    
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 400


@app.route("/api/character-info/history", methods=["GET"])
@login_required
def get_character_info_history_api():
    """Get the change history for character information"""
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    ttrpg_system = request.args.get("ttrpg", "general")
    limit = int(request.args.get("limit", "10"))
    
    history = get_character_info_history(username, ttrpg_system, limit)
    
    return jsonify({
        "username": username,
        "ttrpg_system": ttrpg_system,
        "history": history
    })


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
try:
    # Explicitly get API key to verify it's loaded
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise Exception("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,  # Explicitly pass the API key
        timeout=60.0,     # 60 second timeout (reasonable for complex requests)
        max_retries=2     # Allow 2 retries for temporary failures
    )
    print("✅ OpenAI client initialized successfully with 60s timeout")
except Exception as e:
    print(f"❌ Failed to initialize OpenAI client: {e}")
    client = None

# Initialize messages for backward compatibility with tests
messages = []
# --- OpenAI Model Configuration (override via env) ---
# Primary chat model used for responses
OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-5.0")
# Summary/auxiliary model (defaults to same as chat model if not provided)
OPENAI_SUMMARY_MODEL = os.environ.get("OPENAI_SUMMARY_MODEL", OPENAI_CHAT_MODEL)

print(f"🧠 Using OpenAI chat model: {OPENAI_CHAT_MODEL}")
print(f"📝 Using OpenAI summary model: {OPENAI_SUMMARY_MODEL}")

def _env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")

AI_FALLBACKS_ENABLED = _env_bool("AI_FALLBACKS_ENABLED", False)
print(f"🧩 AI fallbacks enabled: {AI_FALLBACKS_ENABLED}")

# Conservative fallbacks in case configured models are unavailable
# Order matters: prefer lightweight but capable models first.
CHAT_MODEL_FALLBACKS = [
    OPENAI_CHAT_MODEL,
    "gpt-4o-mini",
    "gpt-4o",
]

SUMMARY_MODEL_FALLBACKS = [
    OPENAI_SUMMARY_MODEL,
    "gpt-4o-mini",
]

def _is_model_unavailable_error(exc: Exception) -> bool:
    s = str(exc).lower()
    return any(kw in s for kw in [
        "model",
        "not found",
        "does not exist",
        "unknown",
        "no such model",
        "you do not have access",
        "unsupported",
    ])

def chat_completion_with_fallback(messages, model_candidates, max_tokens=None):
    """Try chat completion across candidate models until one succeeds.
    Returns (content, used_model). Raises last exception if all fail with non-model errors.
    """
    if client is None:
        raise RuntimeError("OpenAI client not initialized")
    last_exc = None
    for mdl in model_candidates:
        if not mdl:
            continue
        try:
            kwargs = {"model": mdl, "messages": messages}
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            print(f"[DEBUG] Trying OpenAI model: {mdl}")
            resp = client.chat.completions.create(**kwargs)
            print(f"[DEBUG] OpenAI call succeeded with model: {mdl}")
            content = resp.choices[0].message.content
            return (content.strip() if content is not None else "", mdl)
        except Exception as e:
            last_exc = e
            if _is_model_unavailable_error(e):
                print(f"[WARN] Model '{mdl}' unavailable, trying next fallback... Error: {e}")
                continue
            # Non-model error: re-raise immediately
            print(f"[ERROR] OpenAI call failed with non-model error on '{mdl}': {type(e).__name__}: {e}")
            raise
    # Exhausted all candidates; if last error exists, raise it, else generic error
    if last_exc:
        print(f"[ERROR] All model candidates failed. Last error: {type(last_exc).__name__}: {last_exc}")
        raise last_exc
    raise RuntimeError("No valid model candidates provided for OpenAI call")


from pathlib import Path

def load_system_prompt(page: str) -> str:
    """Load global prompt first, then append any page-specific prompt.
    For 'dune' page, also append the dune_campaign.txt content."""
    base_prompt_path = Path("system_prompt.txt")
    base_prompt = base_prompt_path.read_text(encoding="utf-8").strip() if base_prompt_path.exists() else ""
    
    page_prompt = ""
    # Minimal page-specific augmentation; keep lightweight
    page = (page or "").lower()
    if page == "dune":
        # If there is a dune campaign file, append trimmed content (optional)
        dune_path = Path("documents/dune_campaign.txt")
        if dune_path.exists():
            try:
                text = dune_path.read_text(encoding="utf-8")
                page_prompt = "\n\n[CAMPAIGN NOTES - DUNE]\n" + text[:3000]
            except Exception:
                page_prompt = ""
    # Combine and return
    return (base_prompt + page_prompt).strip()

def _classify_openai_error(e: Exception) -> Dict[str, Any]:
    """Return a structured classification for OpenAI errors for logging/health checks."""
    cls = type(e).__name__
    info: Dict[str, Any] = {"type": cls, "message": str(e)}
    # Status code if present (APIStatusError)
    try:
        if isinstance(e, APIStatusError):
            info["status_code"] = getattr(e, "status_code", None)
            info["body"] = getattr(e, "response", None)
    except Exception:
        pass
    s = str(e).lower()
    if isinstance(e, AuthenticationError) or "api key" in s:
        info["category"] = "AUTH"
    elif isinstance(e, RateLimitError) or "rate" in s:
        info["category"] = "RATE_LIMIT"
    elif isinstance(e, APITimeoutError) or "timeout" in s:
        info["category"] = "TIMEOUT"
    elif isinstance(e, APIConnectionError) or "connection" in s or "network" in s:
        info["category"] = "NETWORK"
    elif _is_model_unavailable_error(e):
        info["category"] = "MODEL_UNAVAILABLE"
    elif isinstance(e, BadRequestError) or "invalid" in s or "bad request" in s:
        info["category"] = "BAD_REQUEST"
    else:
        info["category"] = "UNKNOWN"
    return info

@app.route("/health/ai")
def health_ai():
    """Active health probe for OpenAI chat with detailed diagnostics."""
    model_chain = CHAT_MODEL_FALLBACKS  # Use configured order, but report per-attempt
    if client is None:
        return jsonify({
            "ok": False,
            "reason": "OPENAI_CLIENT_UNINITIALIZED",
            "models": model_chain,
        }), 200
    attempts = []
    for mdl in model_chain:
        if not mdl:
            continue
        start = datetime.datetime.now()
        try:
            resp = client.chat.completions.create(
                model=mdl,
                messages=[{"role": "system", "content": "Ping"}, {"role": "user", "content": "Ping"}],
                max_tokens=4,
            )
            dur_ms = int((datetime.datetime.now() - start).total_seconds() * 1000)
            attempts.append({"model": mdl, "ok": True, "latency_ms": dur_ms})
            return jsonify({
                "ok": True,
                "used_model": mdl,
                "latency_ms": dur_ms,
                "attempts": attempts,
            }), 200
        except Exception as e:
            info = _classify_openai_error(e)
            dur_ms = int((datetime.datetime.now() - start).total_seconds() * 1000)
            attempts.append({"model": mdl, "ok": False, "latency_ms": dur_ms, "error": info})
            # If it's clearly a non-model error, no need to continue probing
            if info.get("category") in {"AUTH", "NETWORK", "TIMEOUT", "BAD_REQUEST"}:
                break
            # For MODEL_UNAVAILABLE keep trying next
            continue
    return jsonify({
        "ok": False,
        "attempts": attempts,
    }), 200

@app.route("/health/config")
def health_config():
    """Report non-sensitive AI config so we can diagnose issues safely."""
    return jsonify({
        "ok": True,
        "has_openai_key": bool(os.environ.get("OPENAI_API_KEY")),
        "chat_model": OPENAI_CHAT_MODEL,
        "summary_model": OPENAI_SUMMARY_MODEL,
        "fallbacks_enabled": AI_FALLBACKS_ENABLED,
    })
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

# --- Enhanced: Per-user, per-TTRPG chat history ---
def get_user_messages(username, ttrpg_system="general"):
    """Get messages for the current user and TTRPG system"""
    return load_user_messages(username, ttrpg_system)

def save_user_chat(messages, username, ttrpg_system="general"):
    """Save messages for the current user and TTRPG system"""
    save_user_messages(messages, username, ttrpg_system)


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

    try:
        if client is None:
            print("OpenAI client not available for summarization, skipping...")
            return []
            
        if AI_FALLBACKS_ENABLED:
            content, used_model = chat_completion_with_fallback(
                summary_prompt, SUMMARY_MODEL_FALLBACKS
            )
            summary = content
        else:
            if client is None:
                print("OpenAI client not available for summarization, skipping...")
                return []
            resp = client.chat.completions.create(
                model=OPENAI_SUMMARY_MODEL, messages=summary_prompt
            )
            content = resp.choices[0].message.content
            summary = content.strip() if content is not None else ""
        return [{"role": "system", "content": f"SUMMARY OF EARLIER CHAT: {summary}"}]
    except Exception as e:
        print(f"Failed to summarize messages: {e}")
        # Return recent messages without summarization as fallback
        return [m for m in messages if m["role"] in ["user", "assistant"]][-6:]


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def generate_offline_character(ttrpg: str) -> Dict[str, str]:
    """Very small offline generator used when AI is unavailable."""
    ttrpg = (ttrpg or "").lower()
    if "pendragon" in ttrpg:
        names = ["Gareth", "Elowen", "Tristan", "Isolde", "Gawain", "Ysolde"]
        traits = [
            ("Chivalrous", "Brave, Just, Valorous"),
            ("Pious", "Modest, Temperate, Forgiving"),
            ("Worldly", "Proud, Generous, Honest"),
        ]
        weapons = ["Sword", "Lance", "Spear", "Mace"]
        shields = ["Heater", "Kite", "Round"]
        horses = ["Rouncey", "Destrier", "Courser"]
        name = random.choice(names)
        trait, detail = random.choice(traits)
        weapon = random.choice(weapons)
        shield = random.choice(shields)
        horse = random.choice(horses)
        char_info = (
            f"Name: Sir {name}\n"
            f"Culture: Cymric\n"
            f"Traits: {trait} ({detail})\n"
            f"Skills: Sword 15, Lance 13, Courtesy 10, Awareness 12\n"
            f"Glory: 120\n"
            f"Equipment: {weapon}, {shield} Shield, Chain Hauberk, {horse}\n"
            f"Passions: Loyalty (Lord) 14, Love (Family) 12\n"
        )
        notes = (
            "A young knight sworn to a minor lord in Salisbury. Dreams of renown at tourneys and the king's favor."
        )
        return {"character_name": char_info, "character_stats": notes}
    else:
        # Generic fallback
        backgrounds = ["Scholar", "Scout", "Soldier", "Merchant"]
        name = random.choice(["Aria", "Tomas", "Lena", "Borin"])
        bg = random.choice(backgrounds)
        char_info = (
            f"Name: {name}\nBackground: {bg}\nSkills: Investigation 3, Survival 2, Persuasion 2\nGear: Pack, Rations, Cloak"
        )
        notes = "Optimistic and curious. Seeks adventure and hidden lore."
        return {"character_name": char_info, "character_stats": notes}

@app.route("/chat", methods=["POST"])
@cross_origin()  # explicitly allow all origins
def chat():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400

    user_input = data.get("message", "").strip()
    page = data.get("page") or ""
    character_name = data.get("character_name", "").strip()
    character_stats = data.get("character_stats", "").strip()
    
    # Debug: Log exactly what we received
    print(f"[DEBUG] Raw input received:")
    print(f"  user_input: '{user_input}'")
    print(f"  page: '{page}'")
    print(f"  character_name: '{character_name}' (type: {type(character_name)})")
    print(f"  character_stats: '{character_stats}' (type: {type(character_stats)})")
    
    # Input validation for security and compatibility
    if not user_input:
        return jsonify({"error": "Empty input"}), 400
    
    # Basic XSS prevention
    if any(char in user_input for char in ['<', '>', '"', "'", '&']):
        # Clean the input by removing potentially dangerous characters
        user_input = ''.join(char for char in user_input if char not in ['<', '>', '"', "'", '&'])
    
    # Get current user for per-user chat history
    username = current_user.id if current_user.is_authenticated else "Demerzel"
    
    # Update current TTRPG and character info if provided
    if page:
        update_current_ttrpg(page, character_name, character_stats)
    elif not page:
        # Try to determine page from referer
        ref = request.headers.get("Referer", "")
        for candidate in ["the-one-ring", "dune", "call-of-cthulhu", "mouse-guard", "pendragon", "master-template", "ttrpg-chatbot"]:
            if candidate in ref:
                page = candidate
                break
        
        # If still no page, check current TTRPG file
        if not page:
            current_ttrpg_data = load_current_ttrpg()
            page = current_ttrpg_data.get("current_ttrpg", "general")
    
    # Load user-specific, TTRPG-specific chat history
    messages = get_user_messages(username, page)

    # Check if this is a new session (empty chat history) 
    if not messages or len(messages) == 0:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Process character information even for new sessions
        persistent_char_info = load_user_character_info(username, page)
        
        # CRITICAL: Live textbox values ALWAYS take priority over stored values
        char_name = character_name if character_name is not None else persistent_char_info.get("character_name", "")
        char_stats = character_stats if character_stats is not None else persistent_char_info.get("character_stats", "")
        
        # Debug logging for character information priority
        print(f"[DEBUG] Character Info Priority (New Session):")
        print(f"  Live textbox character_name: '{character_name}'")
        print(f"  Live textbox character_stats: '{character_stats}'") 
        print(f"  Stored character_name: '{persistent_char_info.get('character_name', '')}'")
        print(f"  Stored character_stats: '{persistent_char_info.get('character_stats', '')}'")
        print(f"  Final char_name: '{char_name}'")
        print(f"  Final char_stats: '{char_stats}'")
        
        # If user has character information or asks a specific question, don't give generic greeting
        if (char_name or char_stats) or user_input.lower() not in ["", "hello", "hi", "start"]:
            print(f"[DEBUG] User has character info OR asked specific question, processing normally")
            # Process the message normally with character context instead of returning greeting
            pass  # Continue to normal processing
        else:
            # Provide initial greeting for truly new sessions without character info
            ttrpg_titles = {
                "dune": "Dune: Adventures in the Imperium",
                "the-one-ring": "The One Ring",
                "call-of-cthulhu": "Call of Cthulhu",
                "mouse-guard": "Mouse Guard",
                "pendragon": "Pendragon 6th Edition"
            }
            
            ttrpg_worlds = {
                "dune": "the dangerous desert world of Arrakis and the political intrigue of the Imperium",
                "the-one-ring": "Tolkien's Middle-earth",
                "call-of-cthulhu": "the mysterious and horror-filled world of the 1920s",
                "mouse-guard": "the Mouse Territories, where brave mice defend their communities from the dangers of the natural world",
                "pendragon": "Arthurian Britain, the legendary realm of King Arthur, chivalrous knights, and the Round Table"
            }
            
            # Create appropriate initial greeting
            if page in ttrpg_titles:
                greeting = f"Welcome! Would you like to begin a campaign in {ttrpg_worlds[page]}? I can help you create a character and set up your adventure in the world of {ttrpg_titles[page]}."
            else:
                greeting = "Welcome to the TTRPG Chatbot! Please select a game system to begin your adventure."
            
            # Add the greeting as the first message
            messages.append({"role": "assistant", "content": greeting, "timestamp": timestamp})
            save_user_chat(messages, username, page)
            return jsonify({"response": greeting})
    else:
        # For existing sessions, process character information normally
        persistent_char_info = load_user_character_info(username, page)
        
        # CRITICAL: Live textbox values ALWAYS take priority over stored values
        char_name = character_name if character_name is not None else persistent_char_info.get("character_name", "")
        char_stats = character_stats if character_stats is not None else persistent_char_info.get("character_stats", "")
        
        # Debug logging for character information priority
        print(f"[DEBUG] Character Info Priority:")
        print(f"  Live textbox character_name: '{character_name}'")
        print(f"  Live textbox character_stats: '{character_stats}'") 
        print(f"  Stored character_name: '{persistent_char_info.get('character_name', '')}'")
        print(f"  Stored character_stats: '{persistent_char_info.get('character_stats', '')}'")
        print(f"  Final char_name: '{char_name}'")
        print(f"  Final char_stats: '{char_stats}'")

    # ---------- AGENT TAKEOVER FOR DUNE ----------
    if page == "dune":
        session_state = session.get("campaign_state", None)
        result = process_user_request(user_input, session_state, char_name, char_stats)
        session["campaign_state"] = result.get("session_state", {})

        if result.get("takeover", False):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
            messages.append({"role": "assistant", "content": result["response"], "timestamp": timestamp})
            save_user_chat(messages, username, page)
            return jsonify({"response": result["response"]})

        if result.get("response") and not result.get("takeover"):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
            messages.append({"role": "assistant", "content": result["response"], "timestamp": timestamp})
            save_user_chat(messages, username, page)
            return jsonify({"response": result["response"]})
    # -------- END AGENT TAKEOVER SECTION --------


    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages.append({"role": "user", "content": user_input, "timestamp": timestamp})

    # Handle character creation flow
    # Character information has already been processed above (both new and existing sessions)
    
    # Check if user is starting a campaign and needs character creation
    if len(messages) <= 2:  # Only initial greeting and user's first response
        campaign_start_keywords = ["yes", "start", "begin", "campaign", "play", "adventure"]
        character_keywords = ["character", "create", "make", "build", "new"]
        
        if any(keyword in user_input.lower() for keyword in campaign_start_keywords):
            if not char_name and not char_stats:
                ttrpg_titles = {
                    "dune": "Dune: Adventures in the Imperium",
                    "the-one-ring": "The One Ring", 
                    "call-of-cthulhu": "Call of Cthulhu",
                    "mouse-guard": "Mouse Guard",
                    "pendragon": "Pendragon 6th Edition"
                }
                
                char_creation_response = f"Excellent! Before we begin your adventure in {ttrpg_titles.get(page, 'this world')}, let's set up your character. You can either:\n\n1. Create a new character (I can guide you through the process)\n2. Enter existing character information in the Character Information field on the left\n\nWould you like me to help you create a new character, or do you have character details ready to enter?"
                
                messages.append({"role": "assistant", "content": char_creation_response, "timestamp": timestamp})
                save_user_chat(messages, username, page)
                return jsonify({"response": char_creation_response})
        
        # If user mentions character creation without starting campaign
        elif any(keyword in user_input.lower() for keyword in character_keywords):
            if not char_name and not char_stats:
                char_creation_response = f"I'd love to help you create a character! Please tell me what kind of character you'd like to play, or I can guide you through the character creation process step by step. What interests you most about this character?"
                
                messages.append({"role": "assistant", "content": char_creation_response, "timestamp": timestamp})
                save_user_chat(messages, username, page)
                return jsonify({"response": char_creation_response})

    if user_input == "?":
        help_text = "**Available Commands:**\n- `?` – Show this help menu"
        messages.append(
            {"role": "assistant", "content": help_text, "timestamp": timestamp}
        )
        save_user_chat(messages, username, page)
        return jsonify({"response": help_text})

    filtered = [m for m in messages if m["role"] in ["user", "assistant", "system"]]
    system_prompt = load_system_prompt(page)
    full_system_prompt = system_prompt

    # Add character information to the system prompt if available
    # CRITICAL: Use the character information we already determined with proper priority
    # (live textbox values take priority over stored values)
    
    if char_name or char_stats:
        character_context = "\n\n[CURRENT CHARACTER INFORMATION - USE THIS, NOT CHAT HISTORY]\n"
        character_context += "⚠️ CRITICAL: The following is the CURRENT, LIVE character information from the user's textboxes.\n"
        character_context += "ALWAYS use this information instead of any character details mentioned in previous chat messages.\n\n"
        
        if char_name:
            character_context += f"CURRENT Character Information: {char_name}\n"
        if char_stats:
            character_context += f"CURRENT Notes: {char_stats}\n"
        
        character_context += "\n🔥 IMPORTANT: When user asks about character information, refer to the CURRENT values above, not any previous chat history.\n"
        
        print(f"[DEBUG] Character context being added to AI prompt:")
        print(f"  Character Information: '{char_name}'")
        print(f"  Notes: '{char_stats}'")
        print(f"  Full context length: {len(character_context)}")
        
        character_context += """
Use this character information to provide personalized responses and maintain character consistency throughout the conversation.

🔥 AUTOMATIC CHARACTER MANAGEMENT - MANDATORY BEHAVIOR:
YOU MUST AUTOMATICALLY UPDATE CHARACTER INFORMATION AND NOTES WITHOUT BEING ASKED!

⚡ INSTANT UPDATE TRIGGERS (No user request needed):
✅ CHARACTER CREATION: When you create ANY character details → [UPDATE_CHARACTER_INFO] immediately
✅ CHARACTER STATS: When you mention stats, skills, abilities, equipment → [UPDATE_CHARACTER_INFO]  
✅ HEALTH CHANGES: Any damage, healing, status effects → [UPDATE_CHARACTER_INFO]
✅ STORY EVENTS: Important NPCs, plot points, quest info → [UPDATE_NOTES]
✅ CAMPAIGN PROGRESS: Locations visited, choices made, consequences → [UPDATE_NOTES]

⚠️ CRITICAL COMBAT UPDATES:
- DAMAGE/INJURY: Immediately update Character Information with new health status
- HEALING/RECOVERY: Immediately update Character Information with improved health
- EQUIPMENT CHANGES: Immediately update Character Information with new gear
- LEVEL/ADVANCEMENT: Immediately update Character Information with new abilities

📝 STORY TRACKING UPDATES:
- NPC INTRODUCTIONS: Add to Notes with relationships and importance
- QUEST INFORMATION: Add objectives, clues, progress to Notes
- WORLD BUILDING: Add locations, lore, important details to Notes
- PLAYER CHOICES: Track decisions and their consequences in Notes

UPDATE FORMATS (use exactly these):
- Character updates: [UPDATE_CHARACTER_INFO]{updated character details}[/UPDATE_CHARACTER_INFO]
- Story/notes updates: [UPDATE_NOTES]{updated notes}[/UPDATE_NOTES]

🎯 REMEMBER: These updates are AUTOMATIC and MANDATORY - always check if information should be recorded and use update tags immediately without waiting for user requests."""
        
        full_system_prompt += character_context

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

    # Enhanced The One Ring embedding search
    if page == "the-one-ring":
        try:
            print("[DEBUG] Searching The One Ring embeddings...")
            
            # Use memory-optimized search
            search_results = memory_optimized_embedding_search(
                query=user_input,
                system_name="the-one-ring",
                max_results=5,
                min_similarity=0.6
            )
            
            if search_results:
                reference_text = "\n".join([result['text'] for result in search_results])
                full_system_prompt += (
                    f"\n\n[RELEVANT EXCERPTS FROM THE ONE RING RULES]\n"
                    f"Do not reveal or quote these unless the user explicitly asks:\n{reference_text}"
                )
                print(f"[DEBUG] Added {len(reference_text)} chars of The One Ring reference content")
            
        except Exception as e:
            print("The One Ring embedding search failed:", e)

    # Enhanced Dune embedding search
    if page == "dune":
        try:
            print("[DEBUG] Searching Dune embeddings...")
            
            # Use memory-optimized search
            search_results = memory_optimized_embedding_search(
                query=user_input,
                system_name="dune",
                max_results=5,
                min_similarity=0.6
            )
            
            if search_results:
                reference_text = "\n".join([result['text'] for result in search_results])
                full_system_prompt += (
                    f"\n\n[RELEVANT EXCERPTS FROM DUNE RULES]\n"
                    f"Do not reveal or quote these unless the user explicitly asks:\n{reference_text}"
                )
                print(f"[DEBUG] Added {len(reference_text)} chars of Dune reference content")
            
        except Exception as e:
            print("Dune embedding search failed:", e)

    # Enhanced Mouse Guard embedding search
    if page == "mouse-guard":
        try:
            print("[DEBUG] Searching Mouse Guard embeddings...")
            
            # Use memory-optimized search
            search_results = memory_optimized_embedding_search(
                query=user_input,
                system_name="mouse-guard",
                max_results=5,
                min_similarity=0.6
            )
            
            if search_results:
                reference_text = "\n".join([result['text'] for result in search_results])
                full_system_prompt += (
                    f"\n\n[RELEVANT EXCERPTS FROM MOUSE GUARD RULES]\n"
                    f"Do not reveal or quote these unless the user explicitly asks:\n{reference_text}"
                )
                print(f"[DEBUG] Added {len(reference_text)} chars of Mouse Guard reference content")
            
        except Exception as e:
            print("Mouse Guard embedding search failed:", e)

    # Enhanced Pendragon embedding search
    if page == "pendragon":
        try:
            print("[DEBUG] Searching Pendragon embeddings...")
            
            # Use memory-optimized search
            search_results = memory_optimized_embedding_search(
                query=user_input,
                system_name="pendragon",
                max_results=5,
                min_similarity=0.6
            )
            
            if search_results:
                reference_text = "\n".join([result['text'] for result in search_results])
                full_system_prompt += (
                    f"\n\n[RELEVANT EXCERPTS FROM PENDRAGON RULES]\n"
                    f"Do not reveal or quote these unless the user explicitly asks:\n{reference_text}"
                )
                print(f"[DEBUG] Added {len(reference_text)} chars of Pendragon reference content")
            
        except Exception as e:
            print("Pendragon embedding search failed:", e)

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

    try:
        if client is None:
            raise Exception("OpenAI client not properly initialized")
        
        print(f"[DEBUG] Making OpenAI API call with {len(full_messages)} messages...")
        print(f"[DEBUG] System prompt length: {len(full_system_prompt)} characters")
        
        if AI_FALLBACKS_ENABLED:
            content, used_model = chat_completion_with_fallback(
                full_messages, CHAT_MODEL_FALLBACKS, max_tokens=4096
            )
            print(f"[DEBUG] OpenAI API call successful (model: {used_model})")
            trimmed = content
        else:
            # Use only the configured primary model; fail fast if it errors
            if client is None:
                raise RuntimeError("OpenAI client not initialized")
            resp = client.chat.completions.create(
                model=OPENAI_CHAT_MODEL, messages=full_messages, max_tokens=4096
            )
            print(f"[DEBUG] OpenAI API call successful (model: {OPENAI_CHAT_MODEL})")
            content = resp.choices[0].message.content
            trimmed = content.strip() if content is not None else ""
    except Exception as e:
        info = _classify_openai_error(e)
        print(f"OpenAI API call failed: {info}")
        
        # Provide specific error messages based on exception type
        exception_type = type(e).__name__
        if info.get("category") == "TIMEOUT":
            error_message = "⏱️ The AI is taking longer than usual to respond. This sometimes happens with complex requests. Please try again with a shorter message, or wait a moment and retry."
        elif info.get("category") == "RATE_LIMIT":
            error_message = "🚦 The AI service is currently busy. Please wait a moment and try again."
        elif info.get("category") == "NETWORK":
            error_message = "🌐 There's a temporary connection issue with the AI service. Please check your internet connection and try again."
        elif info.get("category") == "AUTH":
            error_message = "🔑 The AI service credentials are not configured correctly on the server. Please check OPENAI_API_KEY."
        elif info.get("category") == "MODEL_UNAVAILABLE":
            error_message = "🧠 The configured model is unavailable. An administrator should choose a supported model or enable fallbacks."
        else:
            # Create a helpful fallback response based on the user input
            user_input_lower = user_input.lower()
            if any(word in user_input_lower for word in ['character', 'create', 'build', 'make']):
                # Offline character generation fallback
                offline = generate_offline_character(page)
                save_user_character_info(username, page, offline["character_name"], offline["character_stats"], source="offline")
                error_message = (
                    "My AI service is temporarily unavailable, so I created a starter character for you. "
                    "You can edit it in the Character Information and Notes on the left, and we can begin right away."
                    "\n\n" + offline["character_name"] + "\n\nNotes: " + offline["character_stats"]
                )
            elif any(word in user_input_lower for word in ['hello', 'hi', 'start', 'begin']):
                error_message = f"Welcome to the TTRPG Chatbot! I'm currently experiencing some technical difficulties but should be back online shortly. In the meantime, you can explore the different game systems and prepare your character information."
            else:
                error_message = "I'm experiencing technical difficulties right now and cannot process your request. Please try again in a moment. If the issue persists, check your internet connection or try refreshing the page."
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messages.append({"role": "assistant", "content": error_message, "timestamp": timestamp})
        save_user_chat(messages, username, page)
        return jsonify({"response": error_message}), 200
    
    # Process AI response for character information updates
    updated_char_info = False
    updated_notes = False
    response_to_send = trimmed
    
    # Check for character information updates
    if "[UPDATE_CHARACTER_INFO]" in trimmed and "[/UPDATE_CHARACTER_INFO]" in trimmed:
        import re
        char_update_match = re.search(r'\[UPDATE_CHARACTER_INFO\](.*?)\[/UPDATE_CHARACTER_INFO\]', trimmed, re.DOTALL)
        if char_update_match:
            new_char_info = char_update_match.group(1).strip()
            
            # Remove any "Character Information:" prefix if present
            if new_char_info.startswith("Character Information:"):
                new_char_info = new_char_info[23:].strip()
            
            print(f"[DEBUG] AI attempting to update character info: {new_char_info[:100]}...")
            
            # Save the updated character information
            success = save_user_character_info(username, page, new_char_info, char_stats, source="ai")
            if success:
                updated_char_info = True
                print(f"[DEBUG] Character info update successful")
                # Remove the update tags from the response
                response_to_send = re.sub(r'\[UPDATE_CHARACTER_INFO\].*?\[/UPDATE_CHARACTER_INFO\]', '', response_to_send, flags=re.DOTALL).strip()
            else:
                print(f"[DEBUG] Character info update failed")
    
    # Check for notes updates
    if "[UPDATE_NOTES]" in trimmed and "[/UPDATE_NOTES]" in trimmed:
        import re
        notes_update_match = re.search(r'\[UPDATE_NOTES\](.*?)\[/UPDATE_NOTES\]', trimmed, re.DOTALL)
        if notes_update_match:
            new_notes = notes_update_match.group(1).strip()
            
            # Remove any "Notes:" prefix if present
            if new_notes.startswith("Notes:"):
                new_notes = new_notes[6:].strip()
            
            print(f"[DEBUG] AI attempting to update notes: {new_notes[:100]}...")
            
            # Save the updated notes (keep existing character info)
            success = save_user_character_info(username, page, char_name, new_notes, source="ai")
            if success:
                updated_notes = True
                print(f"[DEBUG] Notes update successful")
                # Remove the update tags from the response
                response_to_send = re.sub(r'\[UPDATE_NOTES\].*?\[/UPDATE_NOTES\]', '', response_to_send, flags=re.DOTALL).strip()
            else:
                print(f"[DEBUG] Notes update failed")
    
    # Add update notifications to the response if updates were made
    if updated_char_info or updated_notes:
        update_notice = "\n\n*[AI updated: "
        updates = []
        if updated_char_info:
            updates.append("Character Information")
        if updated_notes:
            updates.append("Notes")
        update_notice += " and ".join(updates) + "]*"
        response_to_send += update_notice
    
    messages.append({"role": "assistant", "content": trimmed, "timestamp": timestamp})
    save_user_chat(messages, username, page)

    return jsonify({"response": response_to_send})


# Health check endpoint for personal deployment
@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "user_authenticated": current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False
    })

# Register dynamic routes for all TTRPGs
register_dynamic_routes()

@app.route("/api/memory-status")
@login_required
def memory_status():
    """Get current memory status and embedding cache information."""
    try:
        import psutil
        import os
        
        # Get process memory info
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Get embedding cache status
        embedding_status = get_embedding_status()
        
        return jsonify({
            "memory_usage": {
                "rss_mb": memory_info.rss / (1024 * 1024),  # Resident Set Size
                "vms_mb": memory_info.vms / (1024 * 1024),  # Virtual Memory Size
                "percent": process.memory_percent()
            },
            "embedding_cache": embedding_status,
            "optimization_recommendations": _get_memory_recommendations(memory_info.rss / (1024 * 1024))
        })
    except ImportError:
        # Fallback without psutil
        embedding_status = get_embedding_status()
        return jsonify({
            "memory_usage": {"note": "psutil not available for detailed memory monitoring"},
            "embedding_cache": embedding_status,
            "optimization_recommendations": ["Install psutil for detailed memory monitoring"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clear-cache", methods=["POST"])
@login_required
def clear_cache():
    """Clear embedding cache to free memory."""
    try:
        clear_embedding_cache()
        import gc
        gc.collect()
        
        return jsonify({
            "success": True,
            "message": "Embedding cache cleared and garbage collection performed"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _get_memory_recommendations(memory_mb: float) -> list:
    """Get memory optimization recommendations based on current usage."""
    recommendations = []
    
    if memory_mb > 400:  # Close to 512MB limit
        recommendations.extend([
            "Memory usage is high (over 400MB)",
            "Consider clearing embedding cache after use",
            "Only load one TTRPG system at a time"
        ])
    elif memory_mb > 300:
        recommendations.append("Memory usage is moderate - consider clearing cache periodically")
    else:
        recommendations.append("Memory usage is acceptable")
    
    return recommendations

if __name__ == "__main__":
    app.run(debug=True, port=5000)
