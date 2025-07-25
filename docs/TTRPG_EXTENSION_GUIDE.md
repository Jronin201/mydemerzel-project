# TTRPG Extensibility Framework

This document describes the framework for easily and safely adding new TTRPGs to the Demerzel TTRPG Chatbot system with full integration and functionality.

## Overview

The Demerzel system uses a modular approach where each TTRPG is represented as a self-contained module with standardized components. Adding a new TTRPG requires creating the necessary files and updating a central configuration.

## TTRPG Module Structure

Each TTRPG follows this directory structure within `/static/`:

```
static/
├── <ttrpg-name>/
│   ├── system_prompt.txt        # Required: TTRPG-specific system prompt
│   ├── index.html              # Optional: Custom landing page
│   ├── css/                    # Optional: Custom styles
│   │   └── style.css
│   ├── images/                 # Optional: TTRPG-specific images
│   └── js/                     # Optional: Custom JavaScript
│       └── custom.js
├── text/                       # Optional: Reference documents
│   └── <ttrpg-name>/
│       └── *.txt
└── ttrpg-config.json          # Central configuration file
```

## Adding a New TTRPG: Step-by-Step Guide

### Step 1: Create the Basic Structure

1. Create the main directory: `/static/<ttrpg-name>/`
2. Create the system prompt file: `/static/<ttrpg-name>/system_prompt.txt`
3. Optionally create reference text directory: `/static/text/<ttrpg-name>/`

### Step 2: Write the System Prompt

The `system_prompt.txt` file defines the AI's behavior for this TTRPG. Follow this template:

```
You are the [Game Master Title] for [TTRPG Name], [brief description of the game].

Tone: [Describe the tone - dark, heroic, mysterious, etc.]

Goals:
- [Primary goal 1]
- [Primary goal 2]
- [Primary goal 3]

Setting Guidelines:
- [Setting-specific instructions]
- [Important themes to emphasize]
- [Terminology to use]

Character Creation:
- [How to guide character creation]
- [Important character elements]

Never break character. This is the world of [TTRPG Name].

Respond only in-character unless asked for out-of-character help.
```

### Step 3: Update Central Configuration

Add the new TTRPG to the central configuration by running the registration script:

```bash
python scripts/register_ttrpg.py --name "new-ttrpg-name" --display-name "New TTRPG Name"
```

Or manually update `ttrpg-config.json`:

```json
{
  "systems": {
    "new-ttrpg-name": {
      "display_name": "New TTRPG Name",
      "description": "Brief description of the TTRPG",
      "active": true,
      "has_custom_page": false,
      "has_embeddings": false,
      "created_date": "2024-01-01",
      "version": "1.0"
    }
  }
}
```

### Step 4: Test Integration

Run the integration test to verify everything works:

```bash
python scripts/test_ttrpg_integration.py --ttrpg new-ttrpg-name
```

## Advanced Features (Optional)

### Custom Landing Page

Create `/static/<ttrpg-name>/index.html` for a custom landing page:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>[TTRPG Name] | Demerzel</title>
    <link rel="stylesheet" href="css/style.css" />
  </head>
  <body>
    <div class="container">
      <h1>[TTRPG Name]</h1>
      <p>[Description]</p>
      <a href="/ttrpg-chatbot?ttrpg=<ttrpg-name>" class="start-button"
        >Start Adventure</a
      >
    </div>
  </body>
</html>
```

### Reference Documents

Add reference documents in `/static/text/<ttrpg-name>/`:

- Rules summaries
- Character sheets
- Setting information
- Campaign guides

### Embeddings for Enhanced AI

Generate embeddings for large reference documents:

```bash
python scripts/generate_embeddings.py --ttrpg <ttrpg-name> --source /static/text/<ttrpg-name>/
```

## Backend Integration

The system automatically integrates new TTRPGs through:

1. **Route Generation**: Automatic `/ttrpg-name` route creation
2. **System Prompt Loading**: Automatic loading of `system_prompt.txt`
3. **Character Info**: Per-user, per-TTRPG character persistence
4. **Chat History**: Isolated chat history per TTRPG
5. **API Endpoints**: All existing API endpoints work with new TTRPGs

## File Specifications

### system_prompt.txt Requirements

- **Encoding**: UTF-8
- **Length**: 500-2000 characters recommended
- **Format**: Plain text
- **Content**: Must define AI personality, tone, goals, and behavior

### Directory Naming

- Use lowercase with hyphens: `call-of-cthulhu`, `vampire-the-masquerade`
- No spaces or special characters
- Keep names concise but descriptive

### Configuration Schema

```json
{
  "display_name": "Human-readable name",
  "description": "Brief description (optional)",
  "active": true|false,
  "has_custom_page": true|false,
  "has_embeddings": true|false,
  "created_date": "YYYY-MM-DD",
  "version": "X.Y"
}
```

## Testing and Validation

### Required Tests

1. **System Prompt Loading**: Verify prompt loads correctly
2. **Character Info**: Test character creation and persistence
3. **Chat Integration**: Verify isolated chat history
4. **API Endpoints**: Test all CRUD operations
5. **Route Access**: Verify direct URL access works

### Test Commands

```bash
# Test basic integration
python scripts/test_ttrpg_integration.py --ttrpg <name>

# Test character persistence
python scripts/test_character_persistence.py --ttrpg <name>

# Test system prompt loading
python scripts/test_system_prompts.py --ttrpg <name>
```

## Safety and Best Practices

### Before Adding a TTRPG

1. **Backup**: Run `backup.sh` to create a system backup
2. **Test Environment**: Test in development before production
3. **Validation**: Use provided test scripts
4. **Documentation**: Update this guide if adding new features

### Content Guidelines

1. **Appropriate Content**: Ensure system prompts are appropriate
2. **No Personal Info**: Don't include personal or sensitive information
3. **Copyright**: Respect intellectual property rights
4. **Family Friendly**: Keep content suitable for all users

### Troubleshooting

Common issues and solutions:

1. **TTRPG Not Appearing**: Check `ttrpg-config.json` syntax
2. **System Prompt Not Loading**: Verify file path and encoding
3. **Chat History Issues**: Check file permissions
4. **Character Info Problems**: Verify user directory structure

## Migration and Updates

### Updating Existing TTRPGs

1. Modify system prompts in place
2. Update version number in configuration
3. Test changes thoroughly
4. Document changes in version history

### Removing TTRPGs

1. Set `"active": false` in configuration
2. Archive files rather than deleting
3. Preserve user data (chat history, character info)

## Conclusion

This framework provides a complete system for extending the Demerzel TTRPG Chatbot with new game systems. The modular design ensures that new TTRPGs integrate seamlessly with all existing functionality while maintaining isolation and data integrity.

For questions or issues, refer to the troubleshooting section or contact the system administrator.
