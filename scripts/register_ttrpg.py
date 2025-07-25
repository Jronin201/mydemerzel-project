#!/usr/bin/env python3
"""
TTRPG Registration Script

This script helps register new TTRPGs in the Demerzel system.
It creates the necessary directory structure and updates configuration.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_ttrpg_config():
    """Load the TTRPG configuration file."""
    config_path = Path("ttrpg-config.json")
    
    if not config_path.exists():
        return {
            "systems": {},
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "total_systems": 0,
                "active_systems": 0
            }
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_ttrpg_config(config):
    """Save the TTRPG configuration file."""
    config["metadata"]["last_updated"] = datetime.now().isoformat()
    config["metadata"]["total_systems"] = len(config["systems"])
    config["metadata"]["active_systems"] = sum(1 for system in config["systems"].values() if system.get("active", True))
    
    with open("ttrpg-config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def create_directory_structure(ttrpg_name):
    """Create the basic directory structure for a new TTRPG."""
    base_path = Path("static") / ttrpg_name
    text_path = Path("static") / "text" / ttrpg_name
    
    # Create directories
    base_path.mkdir(parents=True, exist_ok=True)
    text_path.mkdir(parents=True, exist_ok=True)
    
    # Create optional subdirectories
    (base_path / "css").mkdir(exist_ok=True)
    (base_path / "js").mkdir(exist_ok=True)
    (base_path / "images").mkdir(exist_ok=True)
    
    print(f"✓ Created directory structure for '{ttrpg_name}'")
    return base_path


def create_system_prompt_template(ttrpg_name, display_name, game_master_title, base_path):
    """Create a template system prompt file."""
    template = f"""You are the {game_master_title} for {display_name}, [brief description of the game].

Tone: [Describe the tone - dark, heroic, mysterious, etc.]

Goals:
- [Primary goal 1: How should the AI behave?]
- [Primary goal 2: What atmosphere to create?]
- [Primary goal 3: How to guide players?]

Setting Guidelines:
- [Setting-specific instructions]
- [Important themes to emphasize]
- [Terminology to use]

Character Creation:
- [How to guide character creation]
- [Important character elements to track]
- [Character development guidelines]

Never break character. This is the world of {display_name}.

Respond only in-character unless asked for out-of-character help.
"""
    
    prompt_path = base_path / "system_prompt.txt"
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✓ Created system prompt template at {prompt_path}")


def register_ttrpg(ttrpg_name, display_name, description="", game_master_title="Game Master", themes=None, setting=""):
    """Register a new TTRPG in the system."""
    
    # Validate inputs
    if not ttrpg_name or not display_name:
        print("Error: TTRPG name and display name are required")
        return False
    
    # Load current configuration
    config = load_ttrpg_config()
    
    # Check if TTRPG already exists
    if ttrpg_name in config["systems"]:
        print(f"Warning: TTRPG '{ttrpg_name}' already exists")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            return False
    
    # Create directory structure
    base_path = create_directory_structure(ttrpg_name)
    
    # Create system prompt template
    create_system_prompt_template(ttrpg_name, display_name, game_master_title, base_path)
    
    # Add to configuration
    config["systems"][ttrpg_name] = {
        "display_name": display_name,
        "description": description,
        "active": True,
        "has_custom_page": False,
        "has_embeddings": False,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "version": "1.0",
        "game_master_title": game_master_title,
        "themes": themes or [],
        "setting": setting
    }
    
    # Save configuration
    save_ttrpg_config(config)
    
    print(f"✓ Registered '{display_name}' as '{ttrpg_name}'")
    print(f"✓ Configuration updated")
    
    return True


def list_ttrpgs():
    """List all registered TTRPGs."""
    config = load_ttrpg_config()
    
    if not config["systems"]:
        print("No TTRPGs registered yet.")
        return
    
    print("Registered TTRPGs:")
    print("-" * 50)
    
    for name, system in config["systems"].items():
        status = "Active" if system.get("active", True) else "Inactive"
        print(f"{system['display_name']} ({name})")
        print(f"  Status: {status}")
        print(f"  GM Title: {system.get('game_master_title', 'Game Master')}")
        print(f"  Created: {system.get('created_date', 'Unknown')}")
        if system.get('description'):
            print(f"  Description: {system['description']}")
        print()


def deactivate_ttrpg(ttrpg_name):
    """Deactivate a TTRPG without removing it."""
    config = load_ttrpg_config()
    
    if ttrpg_name not in config["systems"]:
        print(f"Error: TTRPG '{ttrpg_name}' not found")
        return False
    
    config["systems"][ttrpg_name]["active"] = False
    save_ttrpg_config(config)
    
    print(f"✓ Deactivated '{ttrpg_name}'")
    return True


def activate_ttrpg(ttrpg_name):
    """Activate a TTRPG."""
    config = load_ttrpg_config()
    
    if ttrpg_name not in config["systems"]:
        print(f"Error: TTRPG '{ttrpg_name}' not found")
        return False
    
    config["systems"][ttrpg_name]["active"] = True
    save_ttrpg_config(config)
    
    print(f"✓ Activated '{ttrpg_name}'")
    return True


def main():
    parser = argparse.ArgumentParser(description="Register and manage TTRPGs in the Demerzel system")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register a new TTRPG')
    register_parser.add_argument('--name', required=True, help='TTRPG system name (lowercase, hyphens)')
    register_parser.add_argument('--display-name', required=True, help='Human-readable display name')
    register_parser.add_argument('--description', default='', help='Brief description of the TTRPG')
    register_parser.add_argument('--gm-title', default='Game Master', help='Title for the game master (e.g., Keeper, Loremaster)')
    register_parser.add_argument('--themes', nargs='*', help='List of themes (e.g., horror mystery investigation)')
    register_parser.add_argument('--setting', default='', help='Setting description')
    
    # List command
    subparsers.add_parser('list', help='List all registered TTRPGs')
    
    # Activate/Deactivate commands
    activate_parser = subparsers.add_parser('activate', help='Activate a TTRPG')
    activate_parser.add_argument('name', help='TTRPG system name')
    
    deactivate_parser = subparsers.add_parser('deactivate', help='Deactivate a TTRPG')
    deactivate_parser.add_argument('name', help='TTRPG system name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'register':
        success = register_ttrpg(
            args.name, 
            args.display_name, 
            args.description,
            args.gm_title,
            args.themes,
            args.setting
        )
        if success:
            print("\n" + "="*50)
            print("NEXT STEPS:")
            print("="*50)
            print(f"1. Edit the system prompt: static/{args.name}/system_prompt.txt")
            print(f"2. Test the integration: python scripts/test_ttrpg_integration.py --ttrpg {args.name}")
            print(f"3. Add reference documents to: static/text/{args.name}/")
            print(f"4. Generate embeddings (if needed): python scripts/generate_embeddings.py --ttrpg {args.name}")
            print(f"5. Access your TTRPG at: http://localhost:5000/{args.name}")
    
    elif args.command == 'list':
        list_ttrpgs()
    
    elif args.command == 'activate':
        activate_ttrpg(args.name)
    
    elif args.command == 'deactivate':
        deactivate_ttrpg(args.name)


if __name__ == '__main__':
    main()
