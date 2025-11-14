import os
import datetime
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
from token_counter import count_tokens
from message_history import load_messages_from_file, save_messages_to_file
from user_chat_history import save_user_messages, load_user_messages, get_user_chat_sessions
from user_character_info import save_user_character_info, load_user_character_info, get_user_character_sessions, undo_character_info_change, get_character_info_history
import numpy as np
from pathlib import Path
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "scripts"))

try:
    from chatbot_campaign_manager import process_user_request
except ImportError:
    def process_user_request(user_request, session_state=None):
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
# --- FIX: Load embeddings and reference texts globally for all routes ---
the_witcher_embeddings = []
if Path("embeddings/the-witcher.json").exists():
    with open("embeddings/the-witcher.json", "r", encoding="utf-8") as f:
        the_witcher_embeddings = json.load(f)
the_witcher_texts = {}
witcher_dir = os.path.join(app.static_folder or "static", "text", "the-witcher")
if os.path.isdir(witcher_dir):
    for fname in os.listdir(witcher_dir):
        if fname.endswith(".txt"):
            with open(os.path.join(witcher_dir, fname), "r", encoding="utf-8") as f:
                the_witcher_texts[fname] = f.read()

dune_embeddings = []
if Path("embeddings/dune.json").exists():
    with open("embeddings/dune.json", "r", encoding="utf-8") as f:
        dune_embeddings = json.load(f)

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
                "the-witcher": {
                    "display_name": "The Witcher",
                    "description": "Dark fantasy adventures across the Continent amid monsters, mages, and political intrigue",
                    "active": True,
                    "has_custom_page": False,
                    "has_embeddings": True,
                    "created_date": "2024-01-01",
                    "version": "1.0",
                    "game_master_title": "Loremaster"
                },
                "zweihander": {
                    "display_name": "Zweihander",
                    "description": "Plain Gothic investigations and creeping mysteries",
                    "active": True,
                    "has_custom_page": False,
                    "has_embeddings": False,
                    "created_date": "2024-01-01",
                    "version": "1.0",
                    "game_master_title": "Game Master"
                }
            },
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.datetime.now().isoformat(),
                "total_systems": 3,
                "active_systems": 3
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
@app.route("/the-witcher")
@login_required
def the_witcher():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=the-witcher')


@app.route("/the-one-ring")
@login_required
def the_one_ring():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=the-witcher')

@app.route("/dune")
@login_required
def dune():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=dune')

@app.route("/call-of-cthulhu")
@login_required
def call_of_cthulhu():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=zweihander')

@app.route("/master-template")
@login_required
def master_template():
    return redirect(url_for('ttrpg_chatbot') + '?ttrpg=master-template')

# --- API endpoints for TTRPG management ---
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

from pathlib import Path

def load_system_prompt(page: str) -> str:
    """Load global prompt first, then append any page-specific prompt.
    For 'dune' page, also append the dune_campaign.txt content."""
    base_prompt_path = Path("system_prompt.txt")
    base_prompt = base_prompt_path.read_text(encoding="utf-8").strip() if base_prompt_path.exists() else ""
    
    page_prompt = ""
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

    # Allow model override via environment variables
    OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-5.1")
    OPENAI_SUMMARY_MODEL = os.environ.get("OPENAI_SUMMARY_MODEL", OPENAI_CHAT_MODEL)
    response = client.chat.completions.create(
        model=OPENAI_SUMMARY_MODEL, messages=summary_prompt
    )
    content = response.choices[0].message.content
    summary = content.strip() if content is not None else ""
    return [{"role": "system", "content": f"SUMMARY OF EARLIER CHAT: {summary}"}]


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.route("/chat", methods=["POST"])
@cross_origin()  # explicitly allow all origins
def chat():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400

    user_input = data.get("message", "").strip()
    page = data.get("page") or ""
    legacy_slug_map = {
        "the-one-ring": "the-witcher",
    }
    if page in legacy_slug_map:
        page = legacy_slug_map[page]
    character_name = data.get("character_name", "").strip()
    character_stats = data.get("character_stats", "").strip()
    
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
        for candidate in ["the-witcher", "the-one-ring", "dune", "zweihander", "master-template", "ttrpg-chatbot"]:
            if candidate in ref:
                page = candidate
                break
        if page in legacy_slug_map:
            page = legacy_slug_map[page]
        
        # If still no page, check current TTRPG file
        if not page:
            current_ttrpg_data = load_current_ttrpg()
            page = current_ttrpg_data.get("current_ttrpg", "general")
    
    # Load user-specific, TTRPG-specific chat history
    messages = get_user_messages(username, page)

    # Check if this is a new session (empty chat history) and provide initial greeting
    if not messages or len(messages) == 0:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Define TTRPG-specific greetings
        ttrpg_titles = {
            "dune": "Dune: Adventures in the Imperium",
            "the-witcher": "The Witcher",
            "zweihander": "Zweihander"
        }
        
        ttrpg_worlds = {
            "dune": "the dangerous desert world of Arrakis and the political intrigue of the Imperium",
            "the-witcher": "the dangerous, monster-haunted roads of the Continent",
            "zweihander": "a plain gothic mystery full of creeping dread"
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

    # ---------- AGENT TAKEOVER FOR DUNE ----------
    if page == "dune":
        session_state = session.get("campaign_state", None)
        result = process_user_request(user_input, session_state)
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
    persistent_char_info = load_user_character_info(username, page)
    char_name = character_name or persistent_char_info.get("character_name", "")
    char_stats = character_stats or persistent_char_info.get("character_stats", "")
    
    # Check if user is starting a campaign and needs character creation
    if len(messages) <= 2:  # Only initial greeting and user's first response
        campaign_start_keywords = ["yes", "start", "begin", "campaign", "play", "adventure"]
        if any(keyword in user_input.lower() for keyword in campaign_start_keywords):
            if not char_name and not char_stats:
                ttrpg_titles = {
                    "dune": "Dune: Adventures in the Imperium",
                    "the-witcher": "The Witcher", 
                    "zweihander": "Zweihander"
                }
                
                char_creation_response = f"Excellent! Before we begin your adventure in {ttrpg_titles.get(page, 'this world')}, let's set up your character. You can either:\n\n1. Create a new character (I can guide you through the process)\n2. Enter existing character information in the Character Information field on the left\n\nWould you like me to help you create a new character, or do you have character details ready to enter?"
                
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
    # Load persistent character information for this user and TTRPG (TTRPG-specific only)
    persistent_char_info = load_user_character_info(username, page)
    char_name = character_name or persistent_char_info.get("character_name", "")
    char_stats = character_stats or persistent_char_info.get("character_stats", "")
    
    if char_name or char_stats:
        character_context = "\n\n[CHARACTER INFORMATION]\n"
        if char_name:
            character_context += f"Character Information: {char_name}\n"
        if char_stats:
            character_context += f"Notes: {char_stats}\n"
        
        character_context += """
Use this character information to provide personalized responses and maintain character consistency throughout the conversation.

IMPORTANT AI CAPABILITIES:
- You can read and consider the Character Information and Notes sections throughout the gameplay session
- You can update either section when needed for gameplay (e.g., adding new skills learned, tracking injuries, noting important events)
- Character Information section is for: stats, skills, background, abilities, equipment, character details
- Notes section is for: quest progress, relationships, important events, reminders, campaign-specific information
- To update character info, use the format: [UPDATE_CHARACTER_INFO]Character Information: new content[/UPDATE_CHARACTER_INFO]
- To update notes, use the format: [UPDATE_NOTES]Notes: new content[/UPDATE_NOTES]
- Users can ask you to undo recent changes to either section

Example usage:
- After combat: [UPDATE_CHARACTER_INFO]Character Information: Paul Atreides - Level 2 Fighter, HP: 15/20 (injured), gained combat experience[/UPDATE_CHARACTER_INFO]
- Story progress: [UPDATE_NOTES]Notes: Discovered the secret passage in the palace. Lady Jessica trusts us with family secrets. Next: investigate the traitor[/UPDATE_NOTES]
"""
        
        full_system_prompt += character_context

    full_messages_preview = [{"role": "system", "content": full_system_prompt}] + filtered
    if count_tokens(full_messages_preview) > TOKEN_THRESHOLD:
        summary_message = summarize_messages(messages)[0]
        recent = [m for m in messages if m["role"] in ["user", "assistant"]][-12:]
        filtered = [summary_message] + recent
        messages = [summary_message] + recent

    # Add The Witcher reference text if user is on that page
    if page == "the-witcher" and the_witcher_texts:
        parts = []
        total = 0
        trimmed = False
        for name in sorted(the_witcher_texts):
            text = the_witcher_texts[name]
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
            print("Warning: Trimming The Witcher reference text due to size limit")

        reference = "\n\n".join(parts)
        full_system_prompt += (
            "\n\n[REFERENCE TEXT FROM 'The Witcher TTRPG']\n"
            "Do not reveal or quote this unless the user explicitly asks:\n" + reference
        )

    if page == "the-witcher" and the_witcher_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated (Witcher):", bool(user_embedding))

            best = max(
                the_witcher_embeddings,
                key=lambda x: cosine_similarity(user_embedding, x["embedding"]),
            )
            best_text = best["text"]
            best_source = best["source"]
            best_score = cosine_similarity(user_embedding, best["embedding"])
            print(
                f"[DEBUG] Best match (Witcher) from '{best_source}' with similarity score: {best_score:.4f}"
            )

            full_system_prompt += (
                f"\n\n[RELEVANT EXCERPT FROM '{best_source}']\n"
                f"Do not reveal this unless the user explicitly asks:\n{best_text}"
            )
        except Exception as e:
            print("Witcher embedding search failed:", e)

    if page == "dune" and dune_embeddings:
        try:
            embedding_client = OpenAI()
            user_embedding = embedding_client.embeddings.create(
                model="text-embedding-3-small", input=user_input
            ).data[0].embedding
            print("[DEBUG] User embedding generated for Dune:", bool(user_embedding))

            best = max(
                dune_embeddings,
                key=lambda x: cosine_similarity(user_embedding, x["embedding"]),
            )
            best_text = best["text"]
            best_source = best["source"]
            best_score = cosine_similarity(user_embedding, best["embedding"])
            print(
                f"[DEBUG] Best Dune match from '{best_source}' with similarity score: {best_score:.4f}"
            )

            full_system_prompt += (
                f"\n\n[RELEVANT EXCERPT FROM '{best_source}']\n"
                f"Do not reveal this unless the user explicitly asks:\n{best_text}"
            )
        except Exception as e:
            print("Dune embedding search failed:", e)

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
    OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-5.1")
    try:
        OPENAI_MAX_TOKENS = int(os.environ.get("OPENAI_MAX_TOKENS", "20000"))
    except ValueError:
        OPENAI_MAX_TOKENS = 20000
    response = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL, messages=full_messages, max_tokens=OPENAI_MAX_TOKENS
    )
    content = response.choices[0].message.content
    trimmed = content.strip() if content is not None else ""
    
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
            # Remove the "Character Information: " prefix if present
            if new_char_info.startswith("Character Information: "):
                new_char_info = new_char_info[23:]
            
            # Save the updated character information
            success = save_user_character_info(username, page, new_char_info, char_stats, source="ai")
            if success:
                updated_char_info = True
                # Remove the update tags from the response
                response_to_send = re.sub(r'\[UPDATE_CHARACTER_INFO\].*?\[/UPDATE_CHARACTER_INFO\]', '', response_to_send, flags=re.DOTALL).strip()
    
    # Check for notes updates
    if "[UPDATE_NOTES]" in trimmed and "[/UPDATE_NOTES]" in trimmed:
        import re
        notes_update_match = re.search(r'\[UPDATE_NOTES\](.*?)\[/UPDATE_NOTES\]', trimmed, re.DOTALL)
        if notes_update_match:
            new_notes = notes_update_match.group(1).strip()
            # Remove the "Notes: " prefix if present
            if new_notes.startswith("Notes: "):
                new_notes = new_notes[7:]
            
            # Save the updated notes
            success = save_user_character_info(username, page, char_name, new_notes, source="ai")
            if success:
                updated_notes = True
                # Remove the update tags from the response
                response_to_send = re.sub(r'\[UPDATE_NOTES\].*?\[/UPDATE_NOTES\]', '', response_to_send, flags=re.DOTALL).strip()
    
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

if __name__ == "__main__":
    app.run(debug=True)
