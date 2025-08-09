import random
import os
import json
import subprocess

# Predefined randomization tables, edit as needed!
random_elements = {
    "settings": ["Arrakis", "Giedi Prime", "Caladan"],
    "factions": ["House Atreides", "House Harkonnen", "Fremen", "Spacing Guild"],
    "npcs": ["Duke Leto", "Baron Harkonnen", "Paul Atreides"],
    "goals": ["Secure spice trade", "Dismantle enemy power", "Form alliances"],
    "challenges": ["Political betrayal", "Desert storm", "Resource scarcity"]
}

# List of onboarding Q&A steps for campaign creation
campaign_questions = [
    {"key": "setting", "prompt": "Choose a setting (Arrakis, Giedi Prime, Caladan) or type 'random':"},
    {"key": "factions", "prompt": "Name the main faction(s) or type 'random':"},
    {"key": "npc_roles", "prompt": "List a key NPC or type 'random':"},
    {"key": "player_goals", "prompt": "Describe player goals or type 'random':"},
    {"key": "story_challenge", "prompt": "Choose a challenge/conflict or type 'random':"}
]

def select_random(element, choice):
    """Pick a random value unless user supplies a specific one."""
    if not choice or choice.lower() == "random":
        return random.choice(random_elements[element])
    return choice

from openai import OpenAI
import os

# Allow overriding the model used for campaign creation
OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-5.0")

client = OpenAI()

def create_campaign(setting=None, factions=None, npc_roles=None, player_goals=None, story_challenge=None):
    """
    Uses OpenAI's GPT to generate a full, detailed TTRPG campaign based on onboarding answers.
    """
    # Use random selections if any input is 'random' or None
    setting_choice = select_random("settings", setting)
    factions_choice = select_random("factions", factions)
    npc_roles_choice = select_random("npcs", npc_roles)
    player_goals_choice = select_random("goals", player_goals)
    story_challenge_choice = select_random("challenges", story_challenge)

    prompt = f"""
You are an expert TTRPG Game Master designing a campaign using the Dune universe.
Create a detailed campaign with the following parameters:

- Setting: {setting_choice}
- Factions: {factions_choice}
- Key NPCs: {npc_roles_choice}
- Player Goals: {player_goals_choice}
- Major Challenge/Conflict: {story_challenge_choice}

Include:

- A campaign introduction and overview
- Descriptions of important factions and their motivations
- Profiles of key NPCs and their secret motives
- Detailed player goals and possible subplots
- Main story arcs with plot twists and branching paths
- Suggestions for side quests, unique locations, and recurring antagonists
- An opening scene to set the tone and start the campaign

Format the campaign as markdown text with headings and lists.
"""

    response = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are a creative and detailed TTRPG campaign creator."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048,
        temperature=0.7
    )

    campaign_text = response.choices[0].message.content if response.choices else "Unable to generate campaign at this time."

    scenario = {
        "setting": setting_choice,
        "factions": [factions_choice],
        "npc_roles": npc_roles_choice,
        "player_goals": player_goals_choice,
        "story_challenge": story_challenge_choice,
        "campaign_markdown": campaign_text
    }

    return scenario

def save_campaign_to_file(scenario, campaign_file_path):
    """Save scenario dictionary as formatted json to campaign_file_path."""
    with open(campaign_file_path, "w") as f:
        json.dump(scenario, f, indent=2)

def load_campaign_from_file(campaign_file_path):
    if os.path.exists(campaign_file_path):
        with open(campaign_file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

import subprocess
import os

def run_git_commands():
    """Silently add, commit, and push the campaign file."""
    commands = [
        ["git", "add", "dune_campaign.txt"],
        ["git", "commit", "-m", "Auto-save campaign"],
        ["git", "push", "-u", "origin", "main"],
    ]
    for cmd in commands:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def process_user_request(user_request, session_state=None, character_name=None, character_stats=None):
    import logging
    logging.basicConfig(level=logging.DEBUG)

    if session_state is None:
        session_state = {"onboarding": False, "answers": {}, "current_q": 0}

    user_msg = user_request.strip()
    TRIGGERS = ["start a new campaign", "create a new campaign"]

    logging.debug(f"Received user message: '{user_msg}' with session_state: {session_state}")
    logging.debug(f"Character info: name='{character_name}', stats='{character_stats}'")

    # Check if this is the very first interaction (no previous state) AND user has no character info
    if (not session_state.get("has_greeted", False) and 
        not session_state.get("onboarding", False) and 
        user_msg.lower() not in TRIGGERS and
        not character_name and not character_stats):
        
        # Provide initial Dune greeting only if user has no character information
        session_state["has_greeted"] = True
        greeting = ("Welcome to the dangerous world of Dune! Would you like to begin a campaign in "
                   "the dangerous desert world of Arrakis and the political intrigue of the Imperium? "
                   "I can help you create a character and set up your adventure in Dune: Adventures in the Imperium.")
        
        logging.debug("Providing initial Dune greeting")
        return {
            "response": greeting,
            "takeover": True,
            "session_state": session_state,
        }
    
    # If user has character information, don't provide greeting - let normal AI processing handle it
    if character_name or character_stats:
        logging.debug("User has character information - skipping campaign manager")
        return {
            "response": None,
            "takeover": False,
            "session_state": session_state,
        }

    # Check for campaign start keywords in initial responses
    campaign_start_keywords = ["yes", "start", "begin", "campaign", "play", "adventure"]
    if (session_state.get("has_greeted", False) and 
        not session_state.get("onboarding", False) and
        any(keyword in user_msg.lower() for keyword in campaign_start_keywords)):
        
        # User wants to start, provide character creation guidance
        char_creation_response = ("Excellent! Before we begin your adventure in the world of Dune, let's set up your character. "
                                 "You can either:\n\n1. Create a new character (I can guide you through the process)\n"
                                 "2. Enter existing character information in the Character Information field on the left\n\n"
                                 "Would you like me to help you create a new character, or do you have character details ready to enter?")
        
        logging.debug("Providing Dune character creation guidance")
        return {
            "response": char_creation_response,
            "takeover": True,
            "session_state": session_state,
        }

    # Start onboarding if triggered or ongoing
    if user_msg.lower() in TRIGGERS or session_state["onboarding"]:
        if not session_state["onboarding"]:
            session_state["onboarding"] = True
            session_state["current_q"] = 1
            logging.debug("Starting onboarding, sending first prompt")
            return {
                "response": campaign_questions[0]["prompt"],
                "takeover": True,
                "session_state": session_state,
            }

        qidx = session_state.get("current_q", 0)

        # Store user input only if we previously asked a question (qidx > 0)
        if 0 < qidx <= len(campaign_questions):
            prev_key = campaign_questions[qidx - 1]["key"]
            if prev_key not in session_state["answers"]:
                session_state["answers"][prev_key] = user_msg
                logging.debug(f"Stored answer for '{prev_key}': '{user_msg}'")
            else:
                logging.debug(f"Answer for '{prev_key}' already stored as '{session_state['answers'][prev_key]}'")

        # Next question
        if qidx < len(campaign_questions):
            prompt = campaign_questions[qidx]["prompt"]
            session_state["current_q"] = qidx + 1
            logging.debug(f"Asking question {qidx + 1}: {prompt}")
            return {
                "response": prompt,
                "takeover": True,
                "session_state": session_state,
            }

        # All questions answered: create & save campaign
        logging.debug("All questions answered, creating campaign...")
        scenario = create_campaign(**session_state["answers"])
        campaign_text = scenario["campaign_markdown"]

        import subprocess
        import os
        import logging

        def get_git_root():
            try:
                return subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
            except subprocess.CalledProcessError as e:
                logging.error(f"Git root lookup failed: {e}")
                return os.getcwd()
        try:
            project_root = get_git_root()
            campaign_file_path = os.path.join(project_root, "dune_campaign.txt")
            with open(campaign_file_path, "w", encoding="utf-8") as f:
                f.write(campaign_text)
            logging.debug(f"✅ Campaign written to {campaign_file_path}")
            
            if os.path.exists(campaign_file_path):
                logging.debug("✅ Verified: File exists")
            else:
                logging.error("❌ File not found after write!")

            subprocess.run(["git", "add", "dune_campaign.txt"], cwd=project_root)
            subprocess.run(["git", "commit", "-m", "Auto-save Dune campaign"], cwd=project_root)
            subprocess.run(["git", "push"], cwd=project_root)
            logging.debug("✅ Campaign committed to GitHub.")
        except Exception as e:
            logging.error(f"Error while saving campaign: {e}")

            # Reset onboarding state
            session_state = {"onboarding": False, "answers": {}, "current_q": 0}

            return {
                "response": (
                    f"✅ Campaign created and saved to `dune_campaign.txt`!\n\n"
                    f"Here’s a preview:\n\n"
                    f"{scenario['campaign_markdown'][:1000]}...\n\n"
                    f"(Full file is available in your repo.)"
                ),
                "takeover": False,
                "session_state": session_state,
            }

        # Reset onboarding state after successful save
        session_state = {"onboarding": False, "answers": {}, "current_q": 0}

        logging.debug(f"Scenario response payload: {scenario['campaign_markdown'][:200]}")

        try:
            return {
                "response": (
                    f"✅ Campaign created and saved to `dune_campaign.txt`!\n\n"
                    f"Here’s a preview:\n\n"
                    f"{scenario['campaign_markdown'][:1000]}...\n\n"
                    f"(Full file is available in your repo.)"
                ),
                "takeover": False,
                "session_state": session_state,
            }
        except Exception as e:
            logging.error(f"❌ Exception during response build: {e}")
            return {
                "response": "❌ Internal server error while finalizing campaign.",
                "takeover": False,
                "session_state": session_state,
            }

    else:
        # Not onboarding; normal chat processing
        logging.debug("Not onboarding; passing back control")
        return {
            "response": None,
            "takeover": False,
            "session_state": session_state,
        }
