import random
import json

# Predefined randomization tables
random_elements = {
    "settings": ["Arrakis", "Giedi Prime", "Caladan"],
    "factions": ["House Atreides", "House Harkonnen", "Fremen", "Spacing Guild"],
    "npcs": ["Duke Leto", "Baron Harkonnen", "Paul Atreides"],
    "goals": ["Secure spice trade", "Dismantle enemy power", "Form alliances"],
    "challenges": ["Political betrayal", "Desert storm", "Resource scarcity"]
}

def select_random(element, choice):
    # Randomly selects an element if 'random' is chosen by player
    if choice.lower() == "random":
        return random.choice(random_elements[element])
    return choice

def query_player():
    # Ask the player for campaign preferences
    player_preferences = {
        "setting": input("Choose a setting or type 'random' for it to be chosen randomly: "),
        "factions": input("Name the factions involved or type 'random' for them to be chosen randomly: "),
        "npc_roles": input("List key NPCs or type 'random' for them to be chosen randomly: "),
        "player_goals": input("Describe player goals or type 'random' for them to be chosen randomly: "),
        "story_challenge": input("What conflicts or challenges would you prefer, or type 'random': ")
    }
    return player_preferences

def create_campaign():
    # Generate campaign scenario based on player input
    player_input = query_player()
    
    scenario = {
        "setting": select_random("settings", player_input["setting"]),
        "factions": [select_random("factions", player_input["factions"])],
        "npc_roles": select_random("npcs", player_input["npc_roles"]),
        "player_goals": select_random("goals", player_input["player_goals"]),
        "story_challenge": select_random("challenges", player_input["story_challenge"])
    }
    
    scenario["starting_event"] = (
        f"On {scenario['setting']}, amidst tension between {', '.join(scenario['factions'])}, "
        f"the key figure {scenario['npc_roles']} plays a crucial role. "
        f"Objectives include {scenario['player_goals']} against the backdrop of {scenario['story_challenge']}."
    )

    # Placeholder for rule compliance check
    # correction_needed = check_compliance(scenario)
    
    return scenario

if __name__ == "__main__":
    # Test the campaign creation process
    campaign = create_campaign()
    print(json.dumps(campaign, indent=2))