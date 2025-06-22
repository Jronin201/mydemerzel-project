import random
import json
import re
import os
from difflib import SequenceMatcher

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

def similar(a, b):
    # Returns a similarity ratio between two strings
    return SequenceMatcher(None, a, b).ratio()

def check_compliance(scenario, rules_file_path, threshold=0.5):
    """
    Checks the generated campaign scenario for compliance with Dune rules and lore.
    
    Parameters:
    scenario (dict): The generated campaign scenario.
    rules_file_path (str): The path to the Dune rules text file.
    threshold (float): The similarity threshold for considering text as compliant.
    
    Returns:
    compliant (bool): Whether the scenario is compliant.
    corrections (list): List of corrections needed if any.
    """
    try:
        with open(rules_file_path, 'r') as file:
            rules_text = file.read().lower()

        corrections = []
        
        # Helper function to check compliance with a similarity threshold
        def is_compliant(element, text):
            return any(similar(element.lower(), line.strip()) >= threshold for line in text.splitlines())
        
        # Check compliance for each scenario element
        for key in ['setting', 'factions', 'npc_roles', 'player_goals', 'story_challenge']:
            element = scenario.get(key, '')
            if isinstance(element, list):
                for item in element:
                    if not is_compliant(item, rules_text):
                        corrections.append(f"{key[:-1].capitalize()} not found in Dune lore: {item}.")
            else:
                if not is_compliant(element, rules_text):
                    corrections.append(f"{key[:-1].capitalize()} not found in Dune lore: {element}.")
        
        compliant = len(corrections) == 0
        return compliant, corrections

    except FileNotFoundError:
        print("Rules file not found.")
        return False, ["Rules file not available for compliance check."]

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
    
    # Build the path to dune.txt relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rules_file_path = os.path.abspath(os.path.join(script_dir, "../../documents/dune/dune.txt"))
    print(f"DEBUG: Attempting to open rules file at: {rules_file_path}")
    if not os.path.exists(rules_file_path):
        print(f"ERROR: File not found at {rules_file_path}")
    else:
        print(f"File found: {rules_file_path}")
        
    # Rule compliance check
    compliant, corrections = check_compliance(scenario, rules_file_path)
    if not compliant:
        print("Scenario is not compliant with rules. Corrections needed:")
        for correction in corrections:
            print("-", correction)
    else:
        print("Scenario is compliant.")
    
    return scenario

if __name__ == "__main__":
    # Test the campaign creation process
    campaign = create_campaign()
    print(json.dumps(campaign, indent=2))
