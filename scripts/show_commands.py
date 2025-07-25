#!/usr/bin/env python3
"""
Quick Commands Overview

Shows all available ease-of-use commands in the Demerzel project.
"""

def print_section(title, commands):
    """Print a formatted section of commands."""
    print(f"\n🔹 {title}")
    print("-" * (len(title) + 3))
    for cmd, desc in commands.items():
        print(f"  {cmd}")
        if desc:
            print(f"    → {desc}")
        print()

def main():
    print("🚀 DEMERZEL PROJECT - AVAILABLE COMMANDS")
    print("=" * 50)
    
    # TTRPG Management
    ttrpg_commands = {
        "python scripts/register_ttrpg.py register --name 'system' --display-name 'Name'": "Register new TTRPG",
        "python scripts/register_ttrpg.py list": "List all TTRPGs",
        "python scripts/register_ttrpg.py activate/deactivate system-name": "Enable/disable TTRPG",
        "python scripts/test_ttrpg_integration.py --ttrpg system-name": "Test specific TTRPG",
        "python scripts/test_ttrpg_integration.py": "Test all TTRPGs",
        "python scripts/manage_ttrpg.py validate": "Validate all configurations",
        "python scripts/manage_ttrpg.py backup system-name": "Backup TTRPG data",
        "python scripts/demo_extensibility.py systems": "Show system overview"
    }
    print_section("TTRPG MANAGEMENT", ttrpg_commands)
    
    # Deployment
    deployment_commands = {
        "./start.sh": "Start development server",
        "./deploy.sh": "Deploy to production",
        "./backup.sh": "Full project backup",
        "./security_check.sh": "Security audit",
        "curl http://localhost:5000/health": "Check server health"
    }
    print_section("DEPLOYMENT & SERVER", deployment_commands)
    
    # File Editing
    editing_commands = {
        "nano static/system-name/system_prompt.txt": "Edit TTRPG AI personality",
        "nano ttrpg-config.json": "Edit TTRPG configuration",
        "nano .env": "Edit environment variables",
        "nano docs/TTRPG_EXTENSION_GUIDE.md": "Edit documentation"
    }
    print_section("FILE EDITING", editing_commands)
    
    # Quick Workflows
    workflow_commands = {
        "# ADD NEW TTRPG WORKFLOW": "",
        "python scripts/register_ttrpg.py register --name 'new'": "1. Register system",
        "nano static/new/system_prompt.txt": "2. Edit AI prompt",
        "python scripts/test_ttrpg_integration.py --ttrpg new": "3. Test integration",
        "./deploy.sh": "4. Deploy changes",
        "": "",
        "# TROUBLESHOOTING WORKFLOW": "",
        "python scripts/manage_ttrpg.py validate --ttrpg system": "1. Validate config",
        "python scripts/test_ttrpg_integration.py --ttrpg system": "2. Test integration",
        "cat static/system/system_prompt.txt": "3. Check prompt",
        "python scripts/register_ttrpg.py list": "4. Verify registration"
    }
    print_section("COMMON WORKFLOWS", workflow_commands)
    
    # Quick Access
    print(f"\n🔹 QUICK ACCESS")
    print("-" * 15)
    print("  📚 Complete reference: DEVELOPER_QUICK_REFERENCE.md")
    print("  📖 Extension guide: docs/TTRPG_EXTENSION_GUIDE.md")
    print("  🚀 Deployment guide: DEPLOYMENT.md")
    print("  ⚡ Quick reference: docs/TTRPG_QUICK_REFERENCE.md")
    
    print(f"\n💡 TIP: Add '--help' to any script for detailed options")
    print(f"💡 TIP: Run 'python scripts/demo_extensibility.py' for interactive demos")

if __name__ == '__main__':
    main()
