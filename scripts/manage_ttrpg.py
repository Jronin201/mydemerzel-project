#!/usr/bin/env python3
"""
TTRPG Management Script

This script provides various maintenance and management functions for TTRPGs.
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def backup_ttrpg(ttrpg_name, backup_dir="backups"):
    """Create a backup of a TTRPG's files."""
    backup_path = Path(backup_dir) / f"{ttrpg_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Backup static files
    static_source = Path("static") / ttrpg_name
    if static_source.exists():
        shutil.copytree(static_source, backup_path / "static")
        print(f"✓ Backed up static files")
    
    # Backup text files
    text_source = Path("static") / "text" / ttrpg_name
    if text_source.exists():
        shutil.copytree(text_source, backup_path / "text")
        print(f"✓ Backed up text files")
    
    # Backup embeddings
    embeddings_source = Path("embeddings") / f"{ttrpg_name}.json"
    if embeddings_source.exists():
        shutil.copy2(embeddings_source, backup_path / "embeddings.json")
        print(f"✓ Backed up embeddings")
    
    # Backup user data
    for data_type in ["character_info", "chat_histories"]:
        data_source = Path(data_type) / "anonymous" / ttrpg_name
        if data_source.exists():
            shutil.copytree(data_source, backup_path / data_type)
            print(f"✓ Backed up {data_type}")
    
    print(f"✓ Backup completed: {backup_path}")
    return backup_path


def validate_system_prompt(ttrpg_name):
    """Validate a system prompt file."""
    prompt_path = Path("static") / ttrpg_name / "system_prompt.txt"
    
    if not prompt_path.exists():
        print(f"✗ System prompt not found: {prompt_path}")
        return False
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        issues = []
        
        if len(content) < 100:
            issues.append("System prompt is very short (< 100 characters)")
        
        if len(content) > 3000:
            issues.append("System prompt is very long (> 3000 characters)")
        
        # Check for template placeholders
        placeholders = ["[", "]", "TODO", "FIXME"]
        for placeholder in placeholders:
            if placeholder in content:
                issues.append(f"Contains placeholder text: {placeholder}")
        
        if issues:
            print(f"⚠ System prompt issues for {ttrpg_name}:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"✓ System prompt for {ttrpg_name} is valid ({len(content)} characters)")
            return True
            
    except Exception as e:
        print(f"✗ Error reading system prompt: {e}")
        return False


def validate_all_ttrpgs():
    """Validate all registered TTRPGs."""
    config_path = Path("ttrpg-config.json")
    
    if not config_path.exists():
        print("✗ No TTRPG configuration found")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    systems = config.get("systems", {})
    
    if not systems:
        print("✗ No TTRPGs registered")
        return False
    
    print(f"Validating {len(systems)} TTRPGs...")
    print("-" * 50)
    
    all_valid = True
    
    for ttrpg_name, system_info in systems.items():
        print(f"\n📋 Validating {system_info.get('display_name', ttrpg_name)}:")
        
        # Check if active
        if not system_info.get("active", True):
            print(f"ℹ TTRPG is inactive, skipping validation")
            continue
        
        # Validate directory structure
        static_dir = Path("static") / ttrpg_name
        if not static_dir.exists():
            print(f"✗ Static directory missing: {static_dir}")
            all_valid = False
            continue
        
        # Validate system prompt
        if not validate_system_prompt(ttrpg_name):
            all_valid = False
        
        # Check for optional components
        text_dir = Path("static") / "text" / ttrpg_name
        if text_dir.exists():
            print(f"✓ Text directory found")
        
        embeddings_file = Path("embeddings") / f"{ttrpg_name}.json"
        if embeddings_file.exists():
            print(f"✓ Embeddings file found")
    
    print("\n" + "=" * 50)
    if all_valid:
        print("✓ All TTRPGs passed validation!")
    else:
        print("✗ Some TTRPGs failed validation. Check issues above.")
    
    return all_valid


def clean_inactive_ttrpgs(dry_run=True):
    """Clean up files for inactive TTRPGs."""
    config_path = Path("ttrpg-config.json")
    
    if not config_path.exists():
        print("✗ No TTRPG configuration found")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    systems = config.get("systems", {})
    inactive_systems = [name for name, info in systems.items() if not info.get("active", True)]
    
    if not inactive_systems:
        print("No inactive TTRPGs found.")
        return
    
    print(f"Found {len(inactive_systems)} inactive TTRPGs:")
    for name in inactive_systems:
        display_name = systems[name].get("display_name", name)
        print(f"  - {display_name} ({name})")
    
    if dry_run:
        print("\n(This is a dry run. Use --no-dry-run to actually remove files)")
        return
    
    # Ask for confirmation
    response = input("\nThis will permanently delete files. Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    for ttrpg_name in inactive_systems:
        print(f"\nCleaning {ttrpg_name}...")
        
        # Remove static directory
        static_dir = Path("static") / ttrpg_name
        if static_dir.exists():
            shutil.rmtree(static_dir)
            print(f"✓ Removed static directory")
        
        # Remove text directory
        text_dir = Path("static") / "text" / ttrpg_name
        if text_dir.exists():
            shutil.rmtree(text_dir)
            print(f"✓ Removed text directory")
        
        # Remove embeddings
        embeddings_file = Path("embeddings") / f"{ttrpg_name}.json"
        if embeddings_file.exists():
            embeddings_file.unlink()
            print(f"✓ Removed embeddings file")


def export_ttrpg(ttrpg_name, output_path):
    """Export a TTRPG as a portable package."""
    config_path = Path("ttrpg-config.json")
    
    if not config_path.exists():
        print("✗ No TTRPG configuration found")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if ttrpg_name not in config.get("systems", {}):
        print(f"✗ TTRPG '{ttrpg_name}' not found")
        return False
    
    export_dir = Path(output_path)
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Export configuration
    ttrpg_config = {
        "ttrpg_name": ttrpg_name,
        "system_info": config["systems"][ttrpg_name],
        "export_date": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    with open(export_dir / "ttrpg-package.json", 'w', encoding='utf-8') as f:
        json.dump(ttrpg_config, f, indent=2)
    
    # Copy static files
    static_source = Path("static") / ttrpg_name
    if static_source.exists():
        shutil.copytree(static_source, export_dir / "static")
        print(f"✓ Exported static files")
    
    # Copy text files
    text_source = Path("static") / "text" / ttrpg_name
    if text_source.exists():
        shutil.copytree(text_source, export_dir / "text")
        print(f"✓ Exported text files")
    
    # Copy embeddings
    embeddings_source = Path("embeddings") / f"{ttrpg_name}.json"
    if embeddings_source.exists():
        shutil.copy2(embeddings_source, export_dir / "embeddings.json")
        print(f"✓ Exported embeddings")
    
    print(f"✓ TTRPG package exported to: {export_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Manage TTRPGs in the Demerzel system")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate TTRPG configurations')
    validate_parser.add_argument('--ttrpg', help='Specific TTRPG to validate (optional)')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup a TTRPG')
    backup_parser.add_argument('ttrpg', help='TTRPG name to backup')
    backup_parser.add_argument('--output-dir', default='backups', help='Backup directory')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean inactive TTRPGs')
    clean_parser.add_argument('--no-dry-run', action='store_true', help='Actually remove files')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export a TTRPG package')
    export_parser.add_argument('ttrpg', help='TTRPG name to export')
    export_parser.add_argument('output_path', help='Output directory for export')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'validate':
        if args.ttrpg:
            validate_system_prompt(args.ttrpg)
        else:
            validate_all_ttrpgs()
    
    elif args.command == 'backup':
        backup_ttrpg(args.ttrpg, args.output_dir)
    
    elif args.command == 'clean':
        clean_inactive_ttrpgs(dry_run=not args.no_dry_run)
    
    elif args.command == 'export':
        export_ttrpg(args.ttrpg, args.output_path)


if __name__ == '__main__':
    main()
