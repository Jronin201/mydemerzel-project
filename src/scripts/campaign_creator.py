import random
import json
import re

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

def check_compliance(scenario, rules_file_path):
    """
    Checks the generated campaign scenario for compliance with Dune rules and lore.

    Parameters:
    scenario (dict): The generated campaign scenario.
    rules_file_path (str): The path to the Dune rules text file.

    Returns:
    compliant (bool): Whether the scenario is compliant.
    corrections (list): List of corrections needed if any.
    """
    try:
        with open(rules_file_path, 'r') as file:
            rules_text = file.read()

        corrections = []

        # Check if the setting is mentioned in Dune lore
        setting_compliant = re.search(re.escape(scenario.get('setting', '')), rules_text, re.IGNORECASE) is not None
        if not setting_compliant:
            corrections.append("Setting not found in Dune lore.")

        # Check if all factions are mentioned in Dune lore
        factions = scenario.get('factions', [])
        factions_noncompliant = [f for f in factions if re.search(re.escape(f), rules_text, re.IGNORECASE) is None]
        if factions_noncompliant:
            corrections.append(f"Faction(s) not found in Dune lore: {', '.join(factions_noncompliant)}.")

        # Check if NPC roles are present
        npc_roles = scenario.get('npc_roles', [])
        if isinstance(npc_roles, list):
            npc_roles_noncompliant = [n for n in npc_roles if re.search(re.escape(n), rules_text, re.IGNORECASE) is None]
            if npc_roles_noncompliant:
                corrections.append(f"NPC role(s) not found in Dune lore: {', '.join(npc_roles_noncompliant)}.")
        else:
            if npc_roles and re.search(re.escape(npc_roles), rules_text, re.IGNORECASE) is None:
                corrections.append(f"NPC role not found in Dune lore: {npc_roles}.")

        # Check if player goals are present
        player_goals = scenario.get('player_goals', [])
        if isinstance(player_goals, list):
            goals_noncompliant = [g for g in player_goals if re.search(re.escape(g), rules_text, re.IGNORECASE) is None]
            if goals_noncompliant:
                corrections.append(f"Player goal(s) not found in Dune lore: {', '.join(goals_noncompliant)}.")
        else:
            if player_goals and re.search(re.escape(player_goals), rules_text, re.IGNORECASE) is None:
                corrections.append(f"Player goal not found in Dune lore: {player_goals}.")

        # Check if story challenge is present
        challenge = scenario.get('story_challenge', '')
        if challenge and re.search(re.escape(challenge), rules_text, re.IGNORECASE) is None:
            corrections.append(f"Story challenge not found in Dune lore: {challenge}.")

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

    # Rule compliance check
    compliant, corrections = check_compliance(scenario, 'dune.txt')  # Adjust path as needed

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
