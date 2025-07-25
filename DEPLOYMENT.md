# 🚀 Deployment Guide

## Quick Start Options

### For Development (Fastest)

```bash
./start.sh
```

- Uses Flask development server
- Hot reload enabled
- Debug mode on
- Perfect for testing changes

### For Production Deployment

```bash
./deploy.sh
```

- Uses Gunicorn production server
- Optimized performance
- Production-ready configuration
- Uses minimal dependencies from requirements-prod.txt

### For Development with Production Setup

```bash
./deploy.sh --dev
```

- Uses production dependencies
- But runs Flask dev server
- Good for testing production environment

## TTRPG Extensibility System

This deployment includes a comprehensive system for adding new TTRPGs. See `docs/TTRPG_EXTENSION_GUIDE.md` for complete details.

### Quick TTRPG Addition

1. **Register a new TTRPG:**

   ```bash
   python scripts/register_ttrpg.py register --name "new-system" --display-name "New System" --gm-title "Game Master"
   ```

2. **Edit the system prompt:**

   ```bash
   nano static/new-system/system_prompt.txt
   ```

3. **Test integration:**

   ```bash
   python scripts/test_ttrpg_integration.py --ttrpg new-system
   ```

4. **Restart server to activate new routes:**
   ```bash
   ./deploy.sh  # or ./start.sh for development
   ```

### TTRPG Management Commands

- **List all TTRPGs:** `python scripts/register_ttrpg.py list`
- **Validate all TTRPGs:** `python scripts/manage_ttrpg.py validate`
- **Backup a TTRPG:** `python scripts/manage_ttrpg.py backup <ttrpg-name>`
- **Test integration:** `python scripts/test_ttrpg_integration.py --ttrpg <name>`

## Environment Setup

1. **Copy environment template:**

   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your settings:**

   ```bash
   nano .env  # or your preferred editor
   ```

3. **Required variables:**
   - `FLASK_SECRET_KEY`: Random string for session security
   - `OPENAI_API_KEY`: Your OpenAI API key

## Backup Your Data

Create backups of your character data:

```bash
./backup.sh
```

## Troubleshooting

- **Permission denied**: Run `chmod +x deploy.sh start.sh backup.sh`
- **Missing .env**: Copy from `.env.example` and edit
- **Port in use**: Change port in deploy.sh or kill existing process
- **Dependencies error**: Run `pip install -r requirements-prod.txt`
