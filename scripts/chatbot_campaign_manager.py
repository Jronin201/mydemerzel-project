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

def create_campaign(setting=None, factions=None, npc_roles=None, player_goals=None, story_challenge=None):
    """Assembles a campaign scenario dictionary from given or random answers."""
    scenario = {
        "setting": select_random("settings", setting),
        "factions": [select_random("factions", factions)],
        "npc_roles": select_random("npcs", npc_roles),
        "player_goals": select_random("goals", player_goals),
        "story_challenge": select_random("challenges", story_challenge)
    }
    scenario["starting_event"] = (
        f"On {scenario['setting']}, amidst tension between {', '.join(scenario['factions'])}, "
        f"the key figure {scenario['npc_roles']} plays a crucial role. "
        f"Objectives include {scenario['player_goals']} against the backdrop of {scenario['story_challenge']}."
    )
    return scenario

def save_campaign_to_file(scenario, campaign_file_path):
    """Save scenario dictionary as formatted json to campaign_file_path."""
    with open(campaign_file_path, "w") as f:
        json.dump(scenario, f, indent=2)

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