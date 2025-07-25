import random

def random_choice_from_list(options):
    """
    Randomly selects an item from a given list of options.
    
    Parameters:
    options (list): A list of choices to select from.
    
    Returns:
    The randomly selected choice.
    """
    if not options:
        raise ValueError("Options list must not be empty.")
    return random.choice(options)

def weighted_random_choice(options, weights):
    """
    Randomly selects an item from a list based on weights.
    
    Parameters:
    options (list): A list of choices to select from.
    weights (list): A list of weights corresponding to each choice.
    
    Returns:
    The randomly selected choice.
    """
    if len(options) != len(weights):
        raise ValueError("Options and weights must be of the same length.")
    return random.choices(options, weights=weights, k=1)[0]

def random_element_from_dict(data, key, choice):
    """
    Selects a random element from a dictionary's list based on a given key.
    
    Parameters:
    data (dict): The dictionary containing lists of elements.
    key (str): The key whose list is to be considered.
    choice (str): The player's choice, using 'random' if random selection is desired.
    
    Returns:
    The selected element from the list.
    """
    if choice.lower() == "random":
        return random_choice_from_list(data[key])
    return choice

# Example of use in campaign creation
if __name__ == "__main__":
    # Example options
    example_data = {
        "settings": ["Arrakis", "Giedi Prime", "Caladan"],
        "factions": ["House Atreides", "House Harkonnen", "Fremen", "Spacing Guild"]
    }

    # Example selection
    choice = random_element_from_dict(example_data, "settings", "random")
    print(f"Selected setting: {choice}")