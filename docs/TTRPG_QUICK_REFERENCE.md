# TTRPG Extensibility System - Quick Reference

## What is this system?

The Demerzel TTRPG Chatbot now includes a complete framework for easily adding new tabletop roleplaying games (TTRPGs) with full integration and functionality. Each TTRPG gets:

- ✅ **Isolated chat history** per user, per TTRPG
- ✅ **Persistent character information** with history and undo
- ✅ **Custom AI personality** via system prompts
- ✅ **Automatic route creation** (e.g., `/vampire-the-masquerade`)
- ✅ **Complete API integration** for all features
- ✅ **Validation and testing tools**

## Currently Registered TTRPGs

| Name                     | Display Name                     | GM Title    | Status      |
| ------------------------ | -------------------------------- | ----------- | ----------- |
| `dune`                   | Dune: Adventures in the Imperium | Game Master | ✅ Active   |
| `the-one-ring`           | The One Ring                     | Loremaster  | ✅ Active   |
| `call-of-cthulhu`        | Call of Cthulhu                  | Keeper      | ✅ Active   |
| `vampire-the-masquerade` | Vampire: The Masquerade          | Storyteller | ✅ Active   |
| `master-template`        | Master Template                  | Game Master | ❌ Template |

## Quick Commands

### Adding a New TTRPG

```bash
# Register the system
python scripts/register_ttrpg.py register \
  --name "cyberpunk-red" \
  --display-name "Cyberpunk Red" \
  --description "High-tech, low-life in Night City" \
  --gm-title "Referee" \
  --themes "cyberpunk" "dystopian" "technology"

# Edit the AI personality
nano static/cyberpunk-red/system_prompt.txt

# Test the integration
python scripts/test_ttrpg_integration.py --ttrpg cyberpunk-red

# Restart server to activate
./deploy.sh
```

### Managing TTRPGs

```bash
# List all registered TTRPGs
python scripts/register_ttrpg.py list

# Validate all configurations
python scripts/manage_ttrpg.py validate

# Backup a TTRPG
python scripts/manage_ttrpg.py backup dune

# Deactivate a TTRPG
python scripts/register_ttrpg.py deactivate old-system

# Test all active TTRPGs
python scripts/test_ttrpg_integration.py
```

## File Structure

Each TTRPG creates this structure:

```
static/
├── <ttrpg-name>/
│   ├── system_prompt.txt    # Required: AI personality
│   ├── css/                 # Optional: Custom styles
│   ├── js/                  # Optional: Custom scripts
│   └── images/              # Optional: TTRPG images
├── text/<ttrpg-name>/       # Optional: Reference docs
└── ttrpg-config.json        # Central configuration
```

## Integration Features

Each new TTRPG automatically gets:

1. **Direct URL access**: `http://localhost:5000/<ttrpg-name>`
2. **Chatbot integration**: Works with main chatbot interface
3. **Character management**: Persistent character info with history
4. **Chat isolation**: Separate chat history per TTRPG
5. **API support**: All endpoints work with new TTRPG
6. **Data backup**: Included in backup scripts

## System Prompt Template

```
You are the [GM Title] for [TTRPG Name], [brief description].

Tone: [Describe the desired atmosphere]

Goals:
- [Primary goal 1]
- [Primary goal 2]
- [Primary goal 3]

Setting Guidelines:
- [Important setting rules]
- [Key themes to emphasize]
- [Terminology to use]

Character Creation:
- [Guide character creation process]
- [Important character elements]

Never break character. This is the world of [TTRPG Name].
```

## Testing and Validation

The system includes comprehensive testing:

- **Configuration validation**: Ensures proper setup
- **File structure checks**: Verifies required files exist
- **API integration tests**: Confirms all endpoints work
- **Data isolation tests**: Ensures proper separation
- **Route accessibility**: Verifies URLs work correctly

## Safety Features

- **Backup system**: Easy backup before changes
- **Validation tools**: Catch issues before deployment
- **Rollback capability**: Can deactivate problematic TTRPGs
- **Data preservation**: User data is never deleted automatically

## Advanced Features

- **Custom embeddings**: For TTRPGs with reference documents
- **Custom landing pages**: Override default interface
- **Themes and styling**: Per-TTRPG visual customization
- **Campaign management**: Integration with campaign tools

## Getting Help

- **Full documentation**: See `docs/TTRPG_EXTENSION_GUIDE.md`
- **Test your setup**: Run integration tests before deployment
- **Validate configuration**: Use management tools to check health
- **Backup first**: Always backup before making changes

---

**Ready to add your first TTRPG?** Start with the quick commands above!
