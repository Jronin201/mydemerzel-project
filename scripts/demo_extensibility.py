#!/usr/bin/env python3
"""
TTRPG Extension Demo Script

This script demonstrates the TTRPG extensibility system by showing
how easy it is to add a new TTRPG with full integration.
"""

import json
import sys
import time
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_step(step_num, description):
    """Print a formatted step."""
    print(f"\n🔹 Step {step_num}: {description}")
    print("-" * 40)


def demo_registration():
    """Demonstrate TTRPG registration."""
    print_header("TTRPG Extensibility System Demo")
    
    print("This demo shows how easy it is to add a new TTRPG to the Demerzel system.")
    print("We'll add 'Shadowrun' as an example.")
    
    print_step(1, "Check current TTRPGs")
    print("Command: python scripts/register_ttrpg.py list")
    print("This shows all currently registered TTRPGs...")
    
    print_step(2, "Register new TTRPG")
    print("Command: python scripts/register_ttrpg.py register \\")
    print("  --name 'shadowrun' \\")
    print("  --display-name 'Shadowrun' \\")
    print("  --description 'Cyberpunk fantasy in 2080s' \\")
    print("  --gm-title 'Game Master' \\")
    print("  --themes 'cyberpunk' 'magic' 'corporate'")
    print("\nThis creates:")
    print("  ✓ Directory structure: static/shadowrun/")
    print("  ✓ System prompt template: static/shadowrun/system_prompt.txt")
    print("  ✓ Configuration entry in ttrpg-config.json")
    print("  ✓ User data directories")
    
    print_step(3, "Customize system prompt")
    print("Edit: static/shadowrun/system_prompt.txt")
    print("Define how the AI should behave for this TTRPG...")
    
    print_step(4, "Test integration")
    print("Command: python scripts/test_ttrpg_integration.py --ttrpg shadowrun")
    print("This validates:")
    print("  ✓ Configuration correctness")
    print("  ✓ File structure")
    print("  ✓ System prompt validity")
    print("  ✓ API integration")
    print("  ✓ Route accessibility")
    
    print_step(5, "Restart server")
    print("Command: ./deploy.sh  # or ./start.sh for development")
    print("This activates the new TTRPG routes and makes it available!")
    
    print_step(6, "Access your new TTRPG")
    print("URL: http://localhost:5000/shadowrun")
    print("The system automatically:")
    print("  ✓ Creates the /shadowrun route")
    print("  ✓ Loads the custom system prompt")
    print("  ✓ Isolates chat history")
    print("  ✓ Manages character info")
    print("  ✓ Provides full API access")


def show_current_systems():
    """Show currently registered systems."""
    print_header("Currently Registered TTRPGs")
    
    config_path = Path("ttrpg-config.json")
    
    if not config_path.exists():
        print("No TTRPG configuration found.")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    systems = config.get("systems", {})
    
    if not systems:
        print("No TTRPGs registered.")
        return
    
    print(f"Total systems: {len(systems)}")
    print(f"Active systems: {sum(1 for s in systems.values() if s.get('active', True))}")
    print()
    
    for name, info in systems.items():
        status = "🟢 Active" if info.get("active", True) else "🔴 Inactive"
        print(f"{status} {info.get('display_name', name)} ({name})")
        print(f"   GM Title: {info.get('game_master_title', 'Game Master')}")
        print(f"   URL: http://localhost:5000/{name}")
        if info.get('description'):
            print(f"   Description: {info['description']}")
        print()


def show_features():
    """Show system features."""
    print_header("Extensibility System Features")
    
    features = [
        ("🔧 Easy Registration", "Single command to add new TTRPGs"),
        ("🤖 Custom AI Personality", "System prompts define AI behavior per TTRPG"),
        ("🔗 Automatic Integration", "Routes, APIs, and data management auto-created"),
        ("📊 Isolated Data", "Separate chat history and character info per TTRPG"),
        ("✅ Comprehensive Testing", "Built-in validation and integration tests"),
        ("🛡️ Safety Features", "Backup, rollback, and validation tools"),
        ("📁 Flexible Structure", "Support for custom pages, styles, and documents"),
        ("🔄 Hot Deployment", "Add TTRPGs without system downtime"),
        ("📚 Rich Documentation", "Complete guides and examples"),
        ("🎯 Template System", "Starting templates for new TTRPGs")
    ]
    
    for feature, description in features:
        print(f"{feature}")
        print(f"   {description}")
        print()


def show_file_structure():
    """Show the file structure for TTRPGs."""
    print_header("TTRPG File Structure")
    
    print("Each TTRPG follows this structure:")
    print()
    print("static/")
    print("├── <ttrpg-name>/")
    print("│   ├── system_prompt.txt        # Required: AI personality")
    print("│   ├── index.html              # Optional: Custom landing page")
    print("│   ├── css/                    # Optional: Custom styles")
    print("│   │   └── style.css")
    print("│   ├── images/                 # Optional: TTRPG-specific images")
    print("│   └── js/                     # Optional: Custom JavaScript")
    print("│       └── custom.js")
    print("├── text/                       # Optional: Reference documents")
    print("│   └── <ttrpg-name>/")
    print("│       └── *.txt")
    print("└── ttrpg-config.json          # Central configuration file")
    print()
    print("Additional files:")
    print("├── embeddings/")
    print("│   └── <ttrpg-name>.json      # Optional: AI embeddings")
    print("├── character_info/")
    print("│   └── anonymous/")
    print("│       └── <ttrpg-name>/      # Per-TTRPG character data")
    print("└── chat_histories/")
    print("    └── anonymous/")
    print("        └── <ttrpg-name>/      # Per-TTRPG chat history")


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "systems":
            show_current_systems()
        elif command == "features":
            show_features()
        elif command == "structure":
            show_file_structure()
        elif command == "demo":
            demo_registration()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: demo, systems, features, structure")
    else:
        print("🎮 TTRPG Extensibility System")
        print("============================")
        print()
        print("Available demos:")
        print("  python scripts/demo_extensibility.py demo      # Show registration demo")
        print("  python scripts/demo_extensibility.py systems   # Show current TTRPGs")
        print("  python scripts/demo_extensibility.py features  # Show system features")
        print("  python scripts/demo_extensibility.py structure # Show file structure")
        print()
        print("Quick start:")
        print("  python scripts/register_ttrpg.py list          # List TTRPGs")
        print("  python scripts/manage_ttrpg.py validate        # Validate all")
        print("  python scripts/test_ttrpg_integration.py       # Test all")


if __name__ == '__main__':
    main()
