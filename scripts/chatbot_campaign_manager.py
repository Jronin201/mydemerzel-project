import random
import os
import json

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
        model="gpt-4o",
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

def process_user_request(user_request, session_state=None):
    import logging
    logging.basicConfig(level=logging.DEBUG)

    if session_state is None:
        session_state = {"onboarding": False, "answers": {}, "current_q": 0}

    user_msg = user_request.strip()
    TRIGGERS = ["start a new campaign", "create a new campaign"]

    logging.debug(f"Received user message: '{user_msg}' with session_state: {session_state}")

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
        if qidx > 0 and qidx <= len(campaign_questions):
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
        campaign_file_path = os.path.abspath("dune_campaign.txt")
        save_campaign_to_file(scenario, campaign_file_path)
        logging.debug(f"Campaign saved to {campaign_file_path}")

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

    # Not onboarding; normal chat processing
    logging.debug("Not onboarding; passing back control")
    return {
        "response": None,
        "takeover": False,
        "session_state": session_state,
    }
