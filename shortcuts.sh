#!/bin/bash
# Demerzel Project - Command Shortcuts
# Usage: source shortcuts.sh (to load into current shell)
# Or: ./shortcuts.sh command_name (to run directly)

# TTRPG Management Shortcuts
alias ttrpg-list="python scripts/register_ttrpg.py list"
alias ttrpg-test="python scripts/test_ttrpg_integration.py"
alias ttrpg-validate="python scripts/manage_ttrpg.py validate"
alias ttrpg-demo="python scripts/demo_extensibility.py systems"
alias ttrpg-help="python scripts/show_commands.py"

# Server Management
alias dev-start="./start.sh"
alias prod-deploy="./deploy.sh"
alias server-health="curl -s http://localhost:5000/health | python -m json.tool"

# Quick Access
alias show-commands="python scripts/show_commands.py"
alias quick-ref="cat DEVELOPER_QUICK_REFERENCE.md"

# Function to register new TTRPG with prompts
ttrpg-add() {
    if [ $# -lt 2 ]; then
        echo "Usage: ttrpg-add <system-name> <display-name> [gm-title] [description]"
        echo "Example: ttrpg-add 'shadowrun' 'Shadowrun' 'Game Master' 'Cyberpunk fantasy'"
        return 1
    fi
    
    local name="$1"
    local display="$2"
    local gm_title="${3:-Game Master}"
    local description="${4:-New TTRPG system}"
    
    echo "🎮 Registering TTRPG: $display"
    python scripts/register_ttrpg.py register \
        --name "$name" \
        --display-name "$display" \
        --gm-title "$gm_title" \
        --description "$description"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Registration complete! Next steps:"
        echo "1. Edit system prompt: nano static/$name/system_prompt.txt"
        echo "2. Test integration: ttrpg-test --ttrpg $name"
        echo "3. Deploy: prod-deploy"
    fi
}

# Function to test specific TTRPG
ttrpg-test-one() {
    if [ $# -lt 1 ]; then
        echo "Usage: ttrpg-test-one <system-name>"
        return 1
    fi
    python scripts/test_ttrpg_integration.py --ttrpg "$1"
}

# Function to backup specific TTRPG
ttrpg-backup() {
    if [ $# -lt 1 ]; then
        echo "Usage: ttrpg-backup <system-name>"
        return 1
    fi
    python scripts/manage_ttrpg.py backup "$1"
}

# Function to edit system prompt
ttrpg-edit() {
    if [ $# -lt 1 ]; then
        echo "Usage: ttrpg-edit <system-name>"
        return 1
    fi
    
    local prompt_file="static/$1/system_prompt.txt"
    if [ -f "$prompt_file" ]; then
        nano "$prompt_file"
    else
        echo "❌ System prompt not found: $prompt_file"
        echo "💡 Available systems:"
        ttrpg-list
    fi
}

# Function to show project status
project-status() {
    echo "🚀 DEMERZEL PROJECT STATUS"
    echo "=========================="
    echo ""
    echo "📊 TTRPGs:"
    python scripts/register_ttrpg.py list | grep -E "(Active|Inactive)" | head -10
    echo ""
    echo "🖥️  Server:"
    if curl -s http://localhost:5000/health >/dev/null 2>&1; then
        echo "  ✅ Running ($(curl -s http://localhost:5000/health | python -c 'import json,sys; print(json.load(sys.stdin)["status"])' 2>/dev/null || echo 'unknown'))"
    else
        echo "  ❌ Not running"
    fi
    echo ""
    echo "📁 Files:"
    echo "  Config: $([ -f ttrpg-config.json ] && echo '✅' || echo '❌') ttrpg-config.json"
    echo "  Scripts: $(ls scripts/*.py 2>/dev/null | wc -l) Python scripts"
    echo "  Docs: $(ls docs/*.md 2>/dev/null | wc -l) documentation files"
}

# If script is called directly (not sourced), run the function
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    case "$1" in
        "status") project-status ;;
        "help") show-commands ;;
        *) 
            echo "Demerzel Project Shortcuts"
            echo "========================="
            echo "To use shortcuts, run: source shortcuts.sh"
            echo "Available shortcuts:"
            echo "  ttrpg-list, ttrpg-test, ttrpg-validate, ttrpg-demo"
            echo "  ttrpg-add <name> <display>, ttrpg-edit <name>"
            echo "  dev-start, prod-deploy, server-health"
            echo "  project-status, show-commands"
            ;;
    esac
else
    echo "✅ Demerzel shortcuts loaded!"
    echo "💡 Try: ttrpg-list, project-status, or show-commands"
fi
