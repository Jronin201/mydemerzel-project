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
    """
    Manages onboarding logic and campaign creation.
    Returns a dict: {response: str, takeover: bool, session_state: dict}
    """
    # Defensive: Always start with state
    if session_state is None:
        session_state = {"onboarding": False, "answers": {}, "current_q": 0}

    # Lowercase/normalize input for trigger detection
    user_msg = user_request.strip().lower()
    TRIGGERS = ["start a new campaign", "create a new campaign"]

    # 1. Start takeover if trigger detected or onboarding in progress
    if user_msg in TRIGGERS or session_state.get("onboarding", False):

        # If beginning onboarding
        if not session_state.get("onboarding", False):
            session_state["onboarding"] = True
            session_state["answers"] = {}
            session_state["current_q"] = 0
            return {
                "response": campaign_questions[0]["prompt"],
                "takeover": True,
                "session_state": session_state
            }

        # 2. We're in onboarding: record answer for previous question
        qidx = session_state.get("current_q", 0)
        if qidx > 0 and qidx <= len(campaign_questions):
            prev_key = campaign_questions[qidx-1]["key"]
            session_state["answers"][prev_key] = user_request

        # 3. More questions needed?
        if qidx < len(campaign_questions):
            prompt = campaign_questions[qidx]["prompt"]
            session_state["current_q"] += 1
            return {
                "response": prompt,
                "takeover": True,
                "session_state": session_state
            }
        else:
            # 4. All questions answered, create & save campaign
            scenario = create_campaign(**session_state["answers"])
            campaign_file_path = os.path.abspath("dune_campaign.txt")
            save_campaign_to_file(scenario, campaign_file_path)
            # Reset state so future "start a new campaign" works
            session_state = {"onboarding": False, "answers": {}, "current_q": 0}
            return {
                "response": f"Campaign created!\n\n{scenario['starting_event']}",
                "takeover": False,
                "session_state": session_state
            }

    # Not a campaign trigger; let the calling code use the normal chatbot
    return {
        "response": None,
        "takeover": False,
        "session_state": session_state
    }

# Optional: CLI quick test
if __name__ == "__main__":
    # Stateful Q&A loop
    sess = None
    while True:
        u = input("You: ")
        bot = process_user_request(u, sess)
        print("Bot:", bot["response"])
        sess = bot.get("session_state", {})
        if not bot["takeover"]:
            break