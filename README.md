# Demerzel Project

This repository contains a Flask application with AI-assisted TTRPG (tabletop roleplaying game) chat interfaces. The project is optimized for **Windows 11 PCs** and provides excellent cross-browser compatibility for desktop environments.

## Overview

Unified TTRPG AI assistant using the OpenAI Responses API (GPT-5.2 primary, gpt-4o fallback) with optional SSE streaming, resilience (single backoff retry + fallback, circuit breaker), structured logging, and multi-system narrative/game support.

## Quick Start

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...   # set your key
python app.py
```

Non-stream request (JSON):

```json
{
  "message": "<assistant text>",
  "model": "gpt-5.2-YYYY-MM-DD",
  "usage": { "input_tokens": 123, "output_tokens": 456 },
  "fallback": false,
  "request_id": "resp_abc123"
}
```

SSE done payload (final event):

```json
{
  "model": "gpt-5.2-YYYY-MM-DD",
  "resp_id": "resp_abc123",
  "usage": { "input_tokens": 123, "output_tokens": 456 },
  "fallback": false,
  "latency_ms": 842,
  "breaker_state": "closed",
  "backoff_ms": 0
}
```

## Production Guide

Resilience features: one 429/5xx backoff retry, fallback to gpt-4o on hard errors, circuit breaker (3 fails/60s → 120s open, half-open probe), reasoning-only retry, abort-safe streaming with heartbeat pings.

👉 For the full runbook (envs, SSE, backoff, breaker, deploy): see [PLAYBOOK.md](./PLAYBOOK.md).

## System Requirements

- **Operating System**: Windows 11 (Optimized)
- **Browser**: Modern desktop browsers (Chrome, Firefox, Edge)
- **Monitor**: Standard desktop monitor (1920x1080 or higher recommended)
- **Input**: Keyboard and mouse interface

## Features

### GPT-5.2 Integration & Health

The application now uses the OpenAI Responses API with GPT-5.2 by default.

Env vars:

- `OPENAI_MODEL` (default: `gpt-5.2`)
- `OPENAI_REASONING_EFFORT` (`low|medium|high`, default `medium`)
- `OPENAI_MAX_OUTPUT_TOKENS` (default `20000` / no artificial upper clamp; min enforced 64)
- `OPENAI_TOOL_CHOICE` (default `none`)
- High-effort per-request override: include `{ "high_effort": true }` in /chat JSON body to force `reasoning.effort=high` (higher latency & cost). See PLAYBOOK for near-cap & truncation monitoring.
- `MODEL_CONTEXT_WINDOW` (default `128000`) used for preflight estimation; requests are adjusted or rejected if they would overflow.

Health check:

- `GET /health/ai` performs a minimal GPT-5.2 probe and returns 200 only if a valid `output_text` == `ok` is received.

Fallback:

- Automatic fallback only to `gpt-4o` on hard errors (auth/permission/not found/rate limit/server errors).

### Streaming (SSE)

Optional Server-Sent Events streaming for `/chat` when you set:

```bash
OPENAI_STREAM_RESPONSES=true
```

Client must send `Accept: text/event-stream`.

Events emitted:

- `token` – incremental text delta
- `ping` – heartbeat every ~15s (configurable via `STREAM_HEARTBEAT_INTERVAL` Flask config; first ping is immediate)
- `done` – final metadata JSON: `{"model":"...","resp_id":"resp_...","usage":{"input_tokens":n,"output_tokens":m},"fallback":false}`

Retry & fallback semantics (streaming and non-streaming):

1. First attempt uses configured `OPENAI_MODEL`.
2. If it produces only reasoning (no `token` events) before completion, one automatic retry with low reasoning effort and larger `max_output_tokens` (no fallback here).
3. On hard errors (401/403/404/409/429/5xx or model_not_found), a single fallback attempt with `gpt-4o` if `AI_FALLBACKS_ENABLED=true`.
4. `fallback` flag in `done` event (and JSON mode) indicates whether fallback model was used.

Non-streaming JSON response schema (when streaming disabled or no SSE Accept header):

```json
{
  "message": "<assistant text + footer>",
  "model": "gpt-5.2",
  "usage": { "input_tokens": 123, "output_tokens": 456 },
  "fallback": false,
  "request_id": "resp_..."
}
```

Environment variables summary:

- `OPENAI_MODEL` (primary model, default gpt-5.2)
- `OPENAI_FALLBACK_MODEL` (optional explicit fallback, default gpt-4o)
- `OPENAI_REASONING_EFFORT` (low|medium|high; default medium)
- `OPENAI_MAX_OUTPUT_TOKENS` (default 20000; minimum enforced 64; no artificial upper clamp)
- `OPENAI_TOOL_CHOICE` (default none)
- `OPENAI_STREAM_RESPONSES` (enable SSE streaming when true + Accept header)
- `AI_FALLBACKS_ENABLED` (toggle hard-error fallback logic)

Observability:

Structured log lines for `/chat` (JSON mode: `[CHAT] ...`, streaming: `[CHAT_STREAM] ...`) include: model, resp_id, usage input/output tokens, fallback flag, latency_ms (streaming), and attempt outcomes.

- **Multiple Game Systems**: Supports Dune, The One Ring, Zweihander, Mouse Guard, Pendragon, and more
- **PC-Optimized Interface**: Three-column layout designed for desktop monitors
- **Cross-Browser Compatibility**: Works on modern desktop browsers
- **Accessibility**: Full WCAG 2.1 AA compliance with screen reader support
- **Offline Functionality**: Service Worker provides basic offline capabilities
- **Security**: CSP headers and input validation for secure operation
- **Windows 11 Optimized**: Designed specifically for Windows 11 PC environments
- **Quick-Action Buttons**: 20 TTRPG action buttons for rapid gameplay

### Output & Reasoning Defaults

Default max output tokens is 20k with medium reasoning effort. A context window preflight reduces the requested max if combined estimated input + output would exceed the configured window (`MODEL_CONTEXT_WINDOW`). Near-cap (≥95%) and truncation flags (`near_cap`, `truncated`) appear in the enriched SSE `done` event and non‑stream JSON when relevant (see PLAYBOOK for operational responses).

## Browser Compatibility

### Supported Desktop Browsers (Windows 11)

- **Microsoft Edge** (Recommended for Windows 11)
- **Google Chrome 90+**
- **Mozilla Firefox 85+**
- **Opera 75+**

### PC-Optimized Features

- **Grid Layout**: Three-column interface optimized for desktop monitors
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Mouse Interaction**: Hover states and click interactions optimized for mouse use
- **Desktop Fonts**: Font sizes optimized for desktop monitor viewing distances
- **Wide-Screen Support**: Layout scales properly on wide-screen monitors

## Requirements

- Python 3 with the packages from `requirements.txt` (install with `pip install -r requirements.txt`)

## Running

1. Install the Python dependencies: `pip install -r requirements.txt`.

2. **Set up environment variables safely**:

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your actual values (NEVER commit this file)
   # Use a text editor to replace the placeholder values
   ```

   **Required values for `.env`**:

   - `FLASK_SECRET_KEY`: Generate a random string (e.g., using `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `OPENAI_API_KEY`: Your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

3. **Important**: Configure Git to avoid signing issues:

   ```bash
   git config --global commit.gpgsign false
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

4. **Security check** (optional but recommended):

   ```bash
   ./security_check.sh
   ```

5. Start the Flask app:

```bash
python app.py
```

## Deployment

### Standard Deployment

For production deployment, use a WSGI server like Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Note**: For deployment environments, set `DEPLOYMENT_ENV=render` (or your platform) to enable deployment-specific Git configuration.

### Embedding Files Deployment

The project includes large AI embedding files for enhanced TTRPG assistance. Due to GitHub's 100MB file size limit, we provide two deployment options:

#### Option 1: Supabase Storage (Recommended)

Use Supabase to host embedding files for instant deployment:

```bash
# Set Supabase environment variables
export SUPABASE_PROJECT_URL="https://your-project-id.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"

# Download pre-generated embeddings
./scripts/download_embeddings.sh

# Start app
python app.py
```

**Benefits:**

- ✅ Instant deployment (no regeneration needed)
- ✅ Works on locked-down computers
- ✅ No OpenAI API key required for deployment
- ✅ Free tier includes 1GB storage

See [docs/SUPABASE_EMBEDDING_SETUP.md](docs/SUPABASE_EMBEDDING_SETUP.md) for complete setup guide.

#### Option 2: Regenerate Embeddings

Generate fresh embeddings on deployment:

```bash
# Requires OpenAI API key
export OPENAI_API_KEY="your-openai-key"

# Generate embeddings (takes 5-10 minutes)
python generate_optimized_embeddings.py

# Start app
python app.py
```

**Benefits:**

- ✅ Always up-to-date
- ✅ No external dependencies
- ❌ Requires OpenAI API key and credits
- ❌ Takes time to regenerate

Both options provide full TTRPG functionality with AI-enhanced responses.

### Locked-Down Computer Deployment

For deployment on restricted/locked-down computers with limited access:

```bash
# Use the automated lockdown deployment script
./scripts/lockdown_deploy.sh
```

**Features for Restricted Environments:**

- ✅ No admin/root access required
- ✅ Works with limited internet access
- ✅ Automatic dependency installation with --user flag
- ✅ Graceful fallback when embedding files missing
- ✅ Offline functionality (except AI chat responses)

See [docs/LOCKDOWN_DEPLOYMENT.md](docs/LOCKDOWN_DEPLOYMENT.md) for complete lockdown deployment guide.

## Troubleshooting

### Git Issues

If you encounter Git GPG signing errors, see [GIT_SETUP.md](GIT_SETUP.md) for detailed troubleshooting steps.

Quick fix for "gpg failed to sign the data":

```bash
git config --global commit.gpgsign false
```

## Security Features

- Content Security Policy headers
- XSS protection
- Input validation and sanitization
- CSRF protection via Flask-Login
- Secure session management

## Accessibility Features

- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management
- Alternative text for all interactive elements

## File Structure

├── 01 chatgpt simple
├── CHARACTER_TEXTBOX_FIXES.md
├── DEPLOYMENT.md
├── DEPLOYMENT_READY.md
├── DEPLOYMENT_SUCCESS.md
├── DEVELOPER_QUICK_REFERENCE.md
├── EMBEDDING_OPTIMIZATION_SUMMARY.md
├── ENHANCED_FORMATTING_GUIDE.md
├── FORMATTING_IMPLEMENTATION_SUMMARY.md
├── GIT_SETUP.md
├── HORIZONTAL_EXPANSION_COMPLETE.md
├── HORIZONTAL_EXPANSION_FIX.md
├── INTERFACE_UPDATES.md
├── LAYOUT_FIX_SUMMARY.md
├── LOCKDOWN_DEPLOYMENT.md
├── MEMORY_OPTIMIZATION.md
├── OPTIMIZATION_SUCCESS.md
├── README.md
├── RENDER_DEPLOYMENT_FIXED.md
├── **pycache**
│ ├── app.cpython-312.pyc
│ ├── chapter_log.cpython-312.pyc
│ ├── chat_cli.cpython-312.pyc
│ ├── demo_chat_history_system.cpython-312.pyc
│ ├── extract_ring_pdfs.cpython-312.pyc
│ ├── lockdown_embedding_loader.cpython-312.pyc
│ ├── memory_optimized_embeddings.cpython-312.pyc
│ ├── memory_optimized_search.cpython-312.pyc
│ ├── message_history.cpython-312.pyc
│ ├── optimized_embedding_search.cpython-312.pyc
│ ├── split_dune.cpython-312.pyc
│ ├── test_ai_character_integration.cpython-312.pyc
│ ├── test_app_invalid_json.cpython-312.pyc
│ ├── test_character_integration.cpython-312.pyc
│ ├── test_character_live.cpython-312.pyc
│ ├── test_character_persistence.cpython-312.pyc
│ ├── test_chat_history.cpython-312.pyc
│ ├── test_comprehensive_ttrpg.cpython-312.pyc
│ ├── test_final_greeting.cpython-312.pyc
│ ├── test_full_app.cpython-312.pyc
│ ├── test_greeting_system.cpython-312.pyc
│ ├── test_integration.cpython-312.pyc
│ ├── test_interface_updates.cpython-312.pyc
│ ├── test_system_prompts.cpython-312.pyc
│ ├── test_token_counter.cpython-312.pyc
│ ├── test_ttrpg_chat_integration.cpython-312.pyc
│ ├── test_ttrpg_tracking.cpython-312.pyc
│ ├── token_counter.cpython-312.pyc
│ ├── user_character_info.cpython-312.pyc
│ ├── user_chat_history.cpython-312.pyc
│ └── verify_ttrpg_prompts.cpython-312.pyc
├── analyze_embeddings.py
├── app.py
├── app_backup.py
├── backup.sh
├── chapter_log.json
├── chapter_log.py
├── character_info
│ ├── Demerzel
│ │ ├── zweihander_character.json
│ │ ├── dune_character.json
│ │ ├── mouse-guard_character.json
│ │ └── the-one-ring_character.json
│ ├── anonymous
│ │ ├── zweihander
│ │ ├── dune
│ │ ├── the-one-ring
│ │ ├── the-one-ring_character.json
│ │ └── cyberpunk
│ ├── casual_user
│ │ └── dune_character.json
│ ├── detailed_user
│ │ └── dune_character.json
│ ├── hardcore_gamer
│ │ └── dune_character.json
│ └── unlimited_test
│ └── stress_test_character.json
├── chat_cli.py
├── chat_histories
├── current_ttrpg.json
├── demo_chat_history_system.py
├── deploy.sh
├── diagnostics
│ ├── combined.txt
│ ├── diagnostics
│ │ ├── combined.txt
│ │ ├── env.txt
│ │ ├── extensions.txt
│ │ ├── frontend_files.txt
│ │ ├── git.txt
│ │ ├── pip.txt
│ │ ├── py_lines.txt
│ │ ├── python_version.txt
│ │ └── tree.txt
│ ├── env.txt
│ ├── extensions.txt
│ ├── frontend_files.txt
│ ├── git.txt
│ ├── pip.txt
│ ├── py_lines.txt
│ ├── python_version.txt
│ ├── tree.txt
│ └── update.sh
├── docs
│ ├── LOCKDOWN_DEPLOYMENT.md
│ ├── SUPABASE_EMBEDDING_SETUP.md
│ ├── TTRPG_EXTENSION_GUIDE.md
│ ├── TTRPG_QUICK_REFERENCE.md
│ └── index.html
├── documents
│ ├── dune
│ │ └── dune_mechanics.txt
│ ├── mouse-guard
│ │ └── mouse_guard_mechanics.txt
│ └── the-one-ring
│ ├── archive-the-one-ring-starter-adventures.txt
│ ├── archive-the-one-ring-starter-rules.txt
│ ├── desktop.ini
│ ├── the-one-ring-core-rules.pdf
│ └── the-one-ring-starter-shire.pdf
├── embeddings
│ ├── README.md
│ ├── dune_mechanics_v2.json
│ ├── dune_optimized.json
│ ├── test_dune_optimized.json
│ ├── the-one-ring.json
│ └── the-one-ring_optimized.json
├── extract_ring_pdfs.py
├── final_test.py
├── fresh_character_test.py
├── generate_optimized_embeddings.py
├── gunicorn.conf.py
├── lockdown_embedding_loader.py
├── memory_optimized_embeddings.py
├── memory_optimized_search.py
├── message_history.py
├── optimize_embeddings.py
├── optimized_embedding_search.py
├── quick_character_test.py
├── requirements-prod.txt
├── requirements.txt
├── run_all_tests.py
├── run_embedding_optimization.sh
├── scripts
│ ├── **pycache**
│ │ ├── chatbot_campaign_manager.cpython-312.pyc
│ │ ├── extract_dune_text.cpython-312.pyc
│ │ ├── extract_pdf_texts.cpython-312.pyc
│ │ └── generate_embeddings.cpython-312.pyc
│ ├── add_ttrpg_embeddings.sh
│ ├── analyze_dune_embeddings.py
│ ├── chatbot_campaign_manager.py
│ ├── check_supabase_files.sh
│ ├── demo_extensibility.py
│ ├── direct_upload.sh
│ ├── download_embeddings.sh
│ ├── download_mouse_guard_only.sh
│ ├── embed_dune_mechanics.py
│ ├── embed_dune_mechanics_v2.py
│ ├── extract_dune_text.py
│ ├── extract_pdf_texts.py
│ ├── generate_embeddings.py
│ ├── lockdown_deploy.sh
│ ├── manage_ttrpg.py
│ ├── register_ttrpg.py
│ ├── show_commands.py
│ ├── simple_upload.sh
│ ├── test_ttrpg_integration.py
│ └── upload_embeddings.sh
├── security_check.sh
├── shortcuts.sh
├── split_dune.py
├── src
│ └── scripts
│ ├── **pycache**
│ │ └── random_select.cpython-312.pyc
│ └── random_select.py
├── start-optimized.sh
├── start.sh
├── start_optimized.sh
├── start_simple.sh
├── static
│ ├── zweihander
│ │ └── system_prompt.txt
│ ├── dune
│ │ └── system_prompt.txt
│ ├── index.html
│ ├── manifest.json
│ ├── master-template
│ │ ├── index.html
│ │ └── system_prompt.txt
│ ├── mouse-guard
│ │ └── system_prompt.txt
│ ├── pdfjs-backup
│ │ ├── LICENSE
│ │ ├── build
│ │ │ ├── pdf.mjs
│ │ │ ├── pdf.mjs.map
│ │ │ ├── pdf.sandbox.mjs
│ │ │ ├── pdf.sandbox.mjs.map
│ │ │ ├── pdf.worker.mjs
│ │ │ └── pdf.worker.mjs.map
│ │ └── web
│ │ ├── cmaps
│ │ │ ├── 78-EUC-H.bcmap
│ │ │ ├── 78-EUC-V.bcmap
│ │ │ ├── 78-H.bcmap
│ │ │ ├── 78-RKSJ-H.bcmap
│ │ │ ├── 78-RKSJ-V.bcmap
│ │ │ ├── 78-V.bcmap
│ │ │ ├── 78ms-RKSJ-H.bcmap
│ │ │ ├── 78ms-RKSJ-V.bcmap
│ │ │ ├── 83pv-RKSJ-H.bcmap
│ │ │ ├── 90ms-RKSJ-H.bcmap
│ │ │ ├── 90ms-RKSJ-V.bcmap
│ │ │ ├── 90msp-RKSJ-H.bcmap
│ │ │ ├── 90msp-RKSJ-V.bcmap
│ │ │ ├── 90pv-RKSJ-H.bcmap
│ │ │ ├── 90pv-RKSJ-V.bcmap
│ │ │ ├── Add-H.bcmap
│ │ │ ├── Add-RKSJ-H.bcmap
│ │ │ ├── Add-RKSJ-V.bcmap
│ │ │ ├── Add-V.bcmap
│ │ │ ├── Adobe-CNS1-0.bcmap
│ │ │ ├── Adobe-CNS1-1.bcmap
│ │ │ ├── Adobe-CNS1-2.bcmap
│ │ │ ├── Adobe-CNS1-3.bcmap
│ │ │ ├── Adobe-CNS1-4.bcmap
│ │ │ ├── Adobe-CNS1-5.bcmap
│ │ │ ├── Adobe-CNS1-6.bcmap
│ │ │ ├── Adobe-CNS1-UCS2.bcmap
│ │ │ ├── Adobe-GB1-0.bcmap
│ │ │ ├── Adobe-GB1-1.bcmap
│ │ │ ├── Adobe-GB1-2.bcmap
│ │ │ ├── Adobe-GB1-3.bcmap
│ │ │ ├── Adobe-GB1-4.bcmap
│ │ │ ├── Adobe-GB1-5.bcmap
│ │ │ ├── Adobe-GB1-UCS2.bcmap
│ │ │ ├── Adobe-Japan1-0.bcmap
│ │ │ ├── Adobe-Japan1-1.bcmap
│ │ │ ├── Adobe-Japan1-2.bcmap
│ │ │ ├── Adobe-Japan1-3.bcmap
│ │ │ ├── Adobe-Japan1-4.bcmap
│ │ │ ├── Adobe-Japan1-5.bcmap
│ │ │ ├── Adobe-Japan1-6.bcmap
│ │ │ ├── Adobe-Japan1-UCS2.bcmap
│ │ │ ├── Adobe-Korea1-0.bcmap
│ │ │ ├── Adobe-Korea1-1.bcmap
│ │ │ ├── Adobe-Korea1-2.bcmap
│ │ │ ├── Adobe-Korea1-UCS2.bcmap
│ │ │ ├── B5-H.bcmap
│ │ │ ├── B5-V.bcmap
│ │ │ ├── B5pc-H.bcmap
│ │ │ ├── B5pc-V.bcmap
│ │ │ ├── CNS-EUC-H.bcmap
│ │ │ ├── CNS-EUC-V.bcmap
│ │ │ ├── CNS1-H.bcmap
│ │ │ ├── CNS1-V.bcmap
│ │ │ ├── CNS2-H.bcmap
│ │ │ ├── CNS2-V.bcmap
│ │ │ ├── ETHK-B5-H.bcmap
│ │ │ ├── ETHK-B5-V.bcmap
│ │ │ ├── ETen-B5-H.bcmap
│ │ │ ├── ETen-B5-V.bcmap
│ │ │ ├── ETenms-B5-H.bcmap
│ │ │ ├── ETenms-B5-V.bcmap
│ │ │ ├── EUC-H.bcmap
│ │ │ ├── EUC-V.bcmap
│ │ │ ├── Ext-H.bcmap
│ │ │ ├── Ext-RKSJ-H.bcmap
│ │ │ ├── Ext-RKSJ-V.bcmap
│ │ │ ├── Ext-V.bcmap
│ │ │ ├── GB-EUC-H.bcmap
│ │ │ ├── GB-EUC-V.bcmap
│ │ │ ├── GB-H.bcmap
│ │ │ ├── GB-V.bcmap
│ │ │ ├── GBK-EUC-H.bcmap
│ │ │ ├── GBK-EUC-V.bcmap
│ │ │ ├── GBK2K-H.bcmap
│ │ │ ├── GBK2K-V.bcmap
│ │ │ ├── GBKp-EUC-H.bcmap
│ │ │ ├── GBKp-EUC-V.bcmap
│ │ │ ├── GBT-EUC-H.bcmap
│ │ │ ├── GBT-EUC-V.bcmap
│ │ │ ├── GBT-H.bcmap
│ │ │ ├── GBT-V.bcmap
│ │ │ ├── GBTpc-EUC-H.bcmap
│ │ │ ├── GBTpc-EUC-V.bcmap
│ │ │ ├── GBpc-EUC-H.bcmap
│ │ │ ├── GBpc-EUC-V.bcmap
│ │ │ ├── H.bcmap
│ │ │ ├── HKdla-B5-H.bcmap
│ │ │ ├── HKdla-B5-V.bcmap
│ │ │ ├── HKdlb-B5-H.bcmap
│ │ │ ├── HKdlb-B5-V.bcmap
│ │ │ ├── HKgccs-B5-H.bcmap
│ │ │ ├── HKgccs-B5-V.bcmap
│ │ │ ├── HKm314-B5-H.bcmap
│ │ │ ├── HKm314-B5-V.bcmap
│ │ │ ├── HKm471-B5-H.bcmap
│ │ │ ├── HKm471-B5-V.bcmap
│ │ │ ├── HKscs-B5-H.bcmap
│ │ │ ├── HKscs-B5-V.bcmap
│ │ │ ├── Hankaku.bcmap
│ │ │ ├── Hiragana.bcmap
│ │ │ ├── KSC-EUC-H.bcmap
│ │ │ ├── KSC-EUC-V.bcmap
│ │ │ ├── KSC-H.bcmap
│ │ │ ├── KSC-Johab-H.bcmap
│ │ │ ├── KSC-Johab-V.bcmap
│ │ │ ├── KSC-V.bcmap
│ │ │ ├── KSCms-UHC-H.bcmap
│ │ │ ├── KSCms-UHC-HW-H.bcmap
│ │ │ ├── KSCms-UHC-HW-V.bcmap
│ │ │ ├── KSCms-UHC-V.bcmap
│ │ │ ├── KSCpc-EUC-H.bcmap
│ │ │ ├── KSCpc-EUC-V.bcmap
│ │ │ ├── Katakana.bcmap
│ │ │ ├── LICENSE
│ │ │ ├── NWP-H.bcmap
│ │ │ ├── NWP-V.bcmap
│ │ │ ├── RKSJ-H.bcmap
│ │ │ ├── RKSJ-V.bcmap
│ │ │ ├── Roman.bcmap
│ │ │ ├── UniCNS-UCS2-H.bcmap
│ │ │ ├── UniCNS-UCS2-V.bcmap
│ │ │ ├── UniCNS-UTF16-H.bcmap
│ │ │ ├── UniCNS-UTF16-V.bcmap
│ │ │ ├── UniCNS-UTF32-H.bcmap
│ │ │ ├── UniCNS-UTF32-V.bcmap
│ │ │ ├── UniCNS-UTF8-H.bcmap
│ │ │ ├── UniCNS-UTF8-V.bcmap
│ │ │ ├── UniGB-UCS2-H.bcmap
│ │ │ ├── UniGB-UCS2-V.bcmap
│ │ │ ├── UniGB-UTF16-H.bcmap
│ │ │ ├── UniGB-UTF16-V.bcmap
│ │ │ ├── UniGB-UTF32-H.bcmap
│ │ │ ├── UniGB-UTF32-V.bcmap
│ │ │ ├── UniGB-UTF8-H.bcmap
│ │ │ ├── UniGB-UTF8-V.bcmap
│ │ │ ├── UniJIS-UCS2-H.bcmap
│ │ │ ├── UniJIS-UCS2-HW-H.bcmap
│ │ │ ├── UniJIS-UCS2-HW-V.bcmap
│ │ │ ├── UniJIS-UCS2-V.bcmap
│ │ │ ├── UniJIS-UTF16-H.bcmap
│ │ │ ├── UniJIS-UTF16-V.bcmap
│ │ │ ├── UniJIS-UTF32-H.bcmap
│ │ │ ├── UniJIS-UTF32-V.bcmap
│ │ │ ├── UniJIS-UTF8-H.bcmap
│ │ │ ├── UniJIS-UTF8-V.bcmap
│ │ │ ├── UniJIS2004-UTF16-H.bcmap
│ │ │ ├── UniJIS2004-UTF16-V.bcmap
│ │ │ ├── UniJIS2004-UTF32-H.bcmap
│ │ │ ├── UniJIS2004-UTF32-V.bcmap
│ │ │ ├── UniJIS2004-UTF8-H.bcmap
│ │ │ ├── UniJIS2004-UTF8-V.bcmap
│ │ │ ├── UniJISPro-UCS2-HW-V.bcmap
│ │ │ ├── UniJISPro-UCS2-V.bcmap
│ │ │ ├── UniJISPro-UTF8-V.bcmap
│ │ │ ├── UniJISX0213-UTF32-H.bcmap
│ │ │ ├── UniJISX0213-UTF32-V.bcmap
│ │ │ ├── UniJISX02132004-UTF32-H.bcmap
│ │ │ ├── UniJISX02132004-UTF32-V.bcmap
│ │ │ ├── UniKS-UCS2-H.bcmap
│ │ │ ├── UniKS-UCS2-V.bcmap
│ │ │ ├── UniKS-UTF16-H.bcmap
│ │ │ ├── UniKS-UTF16-V.bcmap
│ │ │ ├── UniKS-UTF32-H.bcmap
│ │ │ ├── UniKS-UTF32-V.bcmap
│ │ │ ├── UniKS-UTF8-H.bcmap
│ │ │ ├── UniKS-UTF8-V.bcmap
│ │ │ ├── V.bcmap
│ │ │ └── WP-Symbol.bcmap
│ │ ├── compressed.tracemonkey-pldi-09.pdf
│ │ ├── debugger.css
│ │ ├── debugger.mjs
│ │ ├── iccs
│ │ │ ├── CGATS001Compat-v2-micro.icc
│ │ │ └── LICENSE
│ │ ├── images
│ │ │ ├── altText_add.svg
│ │ │ ├── altText_disclaimer.svg
│ │ │ ├── altText_done.svg
│ │ │ ├── altText_spinner.svg
│ │ │ ├── altText_warning.svg
│ │ │ ├── annotation-check.svg
│ │ │ ├── annotation-comment.svg
│ │ │ ├── annotation-help.svg
│ │ │ ├── annotation-insert.svg
│ │ │ ├── annotation-key.svg
│ │ │ ├── annotation-newparagraph.svg
│ │ │ ├── annotation-noicon.svg
│ │ │ ├── annotation-note.svg
│ │ │ ├── annotation-paperclip.svg
│ │ │ ├── annotation-paragraph.svg
│ │ │ ├── annotation-pushpin.svg
│ │ │ ├── cursor-editorFreeHighlight.svg
│ │ │ ├── cursor-editorFreeText.svg
│ │ │ ├── cursor-editorInk.svg
│ │ │ ├── cursor-editorTextHighlight.svg
│ │ │ ├── editor-toolbar-delete.svg
│ │ │ ├── editor-toolbar-edit.svg
│ │ │ ├── findbarButton-next.svg
│ │ │ ├── findbarButton-previous.svg
│ │ │ ├── gv-toolbarButton-download.svg
│ │ │ ├── loading-icon.gif
│ │ │ ├── loading.svg
│ │ │ ├── messageBar_closingButton.svg
│ │ │ ├── messageBar_info.svg
│ │ │ ├── messageBar_warning.svg
│ │ │ ├── secondaryToolbarButton-documentProperties.svg
│ │ │ ├── secondaryToolbarButton-firstPage.svg
│ │ │ ├── secondaryToolbarButton-handTool.svg
│ │ │ ├── secondaryToolbarButton-lastPage.svg
│ │ │ ├── secondaryToolbarButton-rotateCcw.svg
│ │ │ ├── secondaryToolbarButton-rotateCw.svg
│ │ │ ├── secondaryToolbarButton-scrollHorizontal.svg
│ │ │ ├── secondaryToolbarButton-scrollPage.svg
│ │ │ ├── secondaryToolbarButton-scrollVertical.svg
│ │ │ ├── secondaryToolbarButton-scrollWrapped.svg
│ │ │ ├── secondaryToolbarButton-selectTool.svg
│ │ │ ├── secondaryToolbarButton-spreadEven.svg
│ │ │ ├── secondaryToolbarButton-spreadNone.svg
│ │ │ ├── secondaryToolbarButton-spreadOdd.svg
│ │ │ ├── toolbarButton-bookmark.svg
│ │ │ ├── toolbarButton-currentOutlineItem.svg
│ │ │ ├── toolbarButton-download.svg
│ │ │ ├── toolbarButton-editorFreeText.svg
│ │ │ ├── toolbarButton-editorHighlight.svg
│ │ │ ├── toolbarButton-editorInk.svg
│ │ │ ├── toolbarButton-editorSignature.svg
│ │ │ ├── toolbarButton-editorStamp.svg
│ │ │ ├── toolbarButton-menuArrow.svg
│ │ │ ├── toolbarButton-openFile.svg
│ │ │ ├── toolbarButton-pageDown.svg
│ │ │ ├── toolbarButton-pageUp.svg
│ │ │ ├── toolbarButton-presentationMode.svg
│ │ │ ├── toolbarButton-print.svg
│ │ │ ├── toolbarButton-search.svg
│ │ │ ├── toolbarButton-secondaryToolbarToggle.svg
│ │ │ ├── toolbarButton-sidebarToggle.svg
│ │ │ ├── toolbarButton-viewAttachments.svg
│ │ │ ├── toolbarButton-viewLayers.svg
│ │ │ ├── toolbarButton-viewOutline.svg
│ │ │ ├── toolbarButton-viewThumbnail.svg
│ │ │ ├── toolbarButton-zoomIn.svg
│ │ │ ├── toolbarButton-zoomOut.svg
│ │ │ ├── treeitem-collapsed.svg
│ │ │ └── treeitem-expanded.svg
│ │ ├── locale
│ │ │ ├── ach
│ │ │ │ └── viewer.ftl
│ │ │ ├── af
│ │ │ │ └── viewer.ftl
│ │ │ ├── an
│ │ │ │ └── viewer.ftl
│ │ │ ├── ar
│ │ │ │ └── viewer.ftl
│ │ │ ├── ast
│ │ │ │ └── viewer.ftl
│ │ │ ├── az
│ │ │ │ └── viewer.ftl
│ │ │ ├── be
│ │ │ │ └── viewer.ftl
│ │ │ ├── bg
│ │ │ │ └── viewer.ftl
│ │ │ ├── bn
│ │ │ │ └── viewer.ftl
│ │ │ ├── bo
│ │ │ │ └── viewer.ftl
│ │ │ ├── br
│ │ │ │ └── viewer.ftl
│ │ │ ├── brx
│ │ │ │ └── viewer.ftl
│ │ │ ├── bs
│ │ │ │ └── viewer.ftl
│ │ │ ├── ca
│ │ │ │ └── viewer.ftl
│ │ │ ├── cak
│ │ │ │ └── viewer.ftl
│ │ │ ├── ckb
│ │ │ │ └── viewer.ftl
│ │ │ ├── cs
│ │ │ │ └── viewer.ftl
│ │ │ ├── cy
│ │ │ │ └── viewer.ftl
│ │ │ ├── da
│ │ │ │ └── viewer.ftl
│ │ │ ├── de
│ │ │ │ └── viewer.ftl
│ │ │ ├── dsb
│ │ │ │ └── viewer.ftl
│ │ │ ├── el
│ │ │ │ └── viewer.ftl
│ │ │ ├── en-CA
│ │ │ │ └── viewer.ftl
│ │ │ ├── en-GB
│ │ │ │ └── viewer.ftl
│ │ │ ├── en-US
│ │ │ │ └── viewer.ftl
│ │ │ ├── eo
│ │ │ │ └── viewer.ftl
│ │ │ ├── es-AR
│ │ │ │ └── viewer.ftl
│ │ │ ├── es-CL
│ │ │ │ └── viewer.ftl
│ │ │ ├── es-ES
│ │ │ │ └── viewer.ftl
│ │ │ ├── es-MX
│ │ │ │ └── viewer.ftl
│ │ │ ├── et
│ │ │ │ └── viewer.ftl
│ │ │ ├── eu
│ │ │ │ └── viewer.ftl
│ │ │ ├── fa
│ │ │ │ └── viewer.ftl
│ │ │ ├── ff
│ │ │ │ └── viewer.ftl
│ │ │ ├── fi
│ │ │ │ └── viewer.ftl
│ │ │ ├── fr
│ │ │ │ └── viewer.ftl
│ │ │ ├── fur
│ │ │ │ └── viewer.ftl
│ │ │ ├── fy-NL
│ │ │ │ └── viewer.ftl
│ │ │ ├── ga-IE
│ │ │ │ └── viewer.ftl
│ │ │ ├── gd
│ │ │ │ └── viewer.ftl
│ │ │ ├── gl
│ │ │ │ └── viewer.ftl
│ │ │ ├── gn
│ │ │ │ └── viewer.ftl
│ │ │ ├── gu-IN
│ │ │ │ └── viewer.ftl
│ │ │ ├── he
│ │ │ │ └── viewer.ftl
│ │ │ ├── hi-IN
│ │ │ │ └── viewer.ftl
│ │ │ ├── hr
│ │ │ │ └── viewer.ftl
│ │ │ ├── hsb
│ │ │ │ └── viewer.ftl
│ │ │ ├── hu
│ │ │ │ └── viewer.ftl
│ │ │ ├── hy-AM
│ │ │ │ └── viewer.ftl
│ │ │ ├── hye
│ │ │ │ └── viewer.ftl
│ │ │ ├── ia
│ │ │ │ └── viewer.ftl
│ │ │ ├── id
│ │ │ │ └── viewer.ftl
│ │ │ ├── is
│ │ │ │ └── viewer.ftl
│ │ │ ├── it
│ │ │ │ └── viewer.ftl
│ │ │ ├── ja
│ │ │ │ └── viewer.ftl
│ │ │ ├── ka
│ │ │ │ └── viewer.ftl
│ │ │ ├── kab
│ │ │ │ └── viewer.ftl
│ │ │ ├── kk
│ │ │ │ └── viewer.ftl
│ │ │ ├── km
│ │ │ │ └── viewer.ftl
│ │ │ ├── kn
│ │ │ │ └── viewer.ftl
│ │ │ ├── ko
│ │ │ │ └── viewer.ftl
│ │ │ ├── lij
│ │ │ │ └── viewer.ftl
│ │ │ ├── lo
│ │ │ │ └── viewer.ftl
│ │ │ ├── locale.json
│ │ │ ├── lt
│ │ │ │ └── viewer.ftl
│ │ │ ├── ltg
│ │ │ │ └── viewer.ftl
│ │ │ ├── lv
│ │ │ │ └── viewer.ftl
│ │ │ ├── meh
│ │ │ │ └── viewer.ftl
│ │ │ ├── mk
│ │ │ │ └── viewer.ftl
│ │ │ ├── ml
│ │ │ │ └── viewer.ftl
│ │ │ ├── mr
│ │ │ │ └── viewer.ftl
│ │ │ ├── ms
│ │ │ │ └── viewer.ftl
│ │ │ ├── my
│ │ │ │ └── viewer.ftl
│ │ │ ├── nb-NO
│ │ │ │ └── viewer.ftl
│ │ │ ├── ne-NP
│ │ │ │ └── viewer.ftl
│ │ │ ├── nl
│ │ │ │ └── viewer.ftl
│ │ │ ├── nn-NO
│ │ │ │ └── viewer.ftl
│ │ │ ├── oc
│ │ │ │ └── viewer.ftl
│ │ │ ├── pa-IN
│ │ │ │ └── viewer.ftl
│ │ │ ├── pl
│ │ │ │ └── viewer.ftl
│ │ │ ├── pt-BR
│ │ │ │ └── viewer.ftl
│ │ │ ├── pt-PT
│ │ │ │ └── viewer.ftl
│ │ │ ├── rm
│ │ │ │ └── viewer.ftl
│ │ │ ├── ro
│ │ │ │ └── viewer.ftl
│ │ │ ├── ru
│ │ │ │ └── viewer.ftl
│ │ │ ├── sat
│ │ │ │ └── viewer.ftl
│ │ │ ├── sc
│ │ │ │ └── viewer.ftl
│ │ │ ├── scn
│ │ │ │ └── viewer.ftl
│ │ │ ├── sco
│ │ │ │ └── viewer.ftl
│ │ │ ├── si
│ │ │ │ └── viewer.ftl
│ │ │ ├── sk
│ │ │ │ └── viewer.ftl
│ │ │ ├── skr
│ │ │ │ └── viewer.ftl
│ │ │ ├── sl
│ │ │ │ └── viewer.ftl
│ │ │ ├── son
│ │ │ │ └── viewer.ftl
│ │ │ ├── sq
│ │ │ │ └── viewer.ftl
│ │ │ ├── sr
│ │ │ │ └── viewer.ftl
│ │ │ ├── sv-SE
│ │ │ │ └── viewer.ftl
│ │ │ ├── szl
│ │ │ │ └── viewer.ftl
│ │ │ ├── ta
│ │ │ │ └── viewer.ftl
│ │ │ ├── te
│ │ │ │ └── viewer.ftl
│ │ │ ├── tg
│ │ │ │ └── viewer.ftl
│ │ │ ├── th
│ │ │ │ └── viewer.ftl
│ │ │ ├── tl
│ │ │ │ └── viewer.ftl
│ │ │ ├── tr
│ │ │ │ └── viewer.ftl
│ │ │ ├── trs
│ │ │ │ └── viewer.ftl
│ │ │ ├── uk
│ │ │ │ └── viewer.ftl
│ │ │ ├── ur
│ │ │ │ └── viewer.ftl
│ │ │ ├── uz
│ │ │ │ └── viewer.ftl
│ │ │ ├── vi
│ │ │ │ └── viewer.ftl
│ │ │ ├── wo
│ │ │ │ └── viewer.ftl
│ │ │ ├── xh
│ │ │ │ └── viewer.ftl
│ │ │ ├── zh-CN
│ │ │ │ └── viewer.ftl
│ │ │ └── zh-TW
│ │ │ └── viewer.ftl
│ │ ├── pdfs
│ │ │ ├── dwarf.pdf
│ │ │ ├── elf.pdf
│ │ │ ├── hobbit.pdf
│ │ │ └── men.pdf
│ │ ├── standard_fonts
│ │ │ ├── FoxitDingbats.pfb
│ │ │ ├── FoxitFixed.pfb
│ │ │ ├── FoxitFixedBold.pfb
│ │ │ ├── FoxitFixedBoldItalic.pfb
│ │ │ ├── FoxitFixedItalic.pfb
│ │ │ ├── FoxitSerif.pfb
│ │ │ ├── FoxitSerifBold.pfb
│ │ │ ├── FoxitSerifBoldItalic.pfb
│ │ │ ├── FoxitSerifItalic.pfb
│ │ │ ├── FoxitSymbol.pfb
│ │ │ ├── LICENSE_FOXIT
│ │ │ ├── LICENSE_LIBERATION
│ │ │ ├── LiberationSans-Bold.ttf
│ │ │ ├── LiberationSans-BoldItalic.ttf
│ │ │ ├── LiberationSans-Italic.ttf
│ │ │ └── LiberationSans-Regular.ttf
│ │ ├── viewer.css
│ │ ├── viewer.html
│ │ ├── viewer.mjs
│ │ ├── viewer.mjs.map
│ │ └── wasm
│ │ ├── LICENSE_OPENJPEG
│ │ ├── LICENSE_PDFJS_OPENJPEG
│ │ ├── LICENSE_PDFJS_QCMS
│ │ ├── LICENSE_QCMS
│ │ ├── openjpeg.wasm
│ │ ├── openjpeg_nowasm_fallback.js
│ │ └── qcms_bg.wasm
│ ├── pendragon
│ │ └── system_prompt.txt
│ ├── robots.txt
│ ├── sw.js
│ ├── text
│ │ ├── the-one-ring
│ │ │ ├── the-one-ring-core-rules.txt
│ │ │ └── the-one-ring-starter-shire.txt
│ │ └── cyberpunk
│ ├── the-one-ring
│ │ ├── css
│ │ │ └── main.css
│ │ ├── images
│ │ │ └── v25_3.png
│ │ ├── index.html
│ │ ├── script.js
│ │ └── system_prompt.txt
│ ├── ttrpg-chatbot
│ │ └── index.html
│ └── cyberpunk
│ ├── css
│ ├── images
│ ├── js
│ └── system_prompt.txt
├── system_prompt.txt
├── system_prompt_fixed.txt
├── templates
│ └── login.html
├── test_ai_character_integration.py
├── test_app_invalid_json.py
├── test_character_integration.py
├── test_character_live.py
├── test_character_persistence.py
├── test_character_textbox_functionality.py
├── test_character_textbox_integration.py
├── test_character_update.py
├── test_character_updates.py
├── test_chat_history.py
├── test_chat_horizontal_expansion.html
├── test_chatbot_fix.py
├── test_comprehensive_ttrpg.py
├── test_enhanced_formatting.py
├── test_final_greeting.py
├── test_final_integration.py
├── test_full_app.py
├── test_greeting_system.py
├── test_horizontal_expansion.html
├── test_integration.py
├── test_interface_updates.py
├── test_layout_positioning.html
├── test_lockdown_integration.py
├── test_memory_optimization.py
├── test_mouse_guard.py
├── test_mouse_guard_knowledge.py
├── test_mouse_guard_loading.py
├── test_one_ring_character.py
├── test_optimized_embeddings.py
├── test_optimized_search.py
├── test_pendragon_integration.py
├── test_system_prompts.py
├── test_token_counter.py
├── test_ttrpg_chat_integration.py
├── test_ttrpg_tracking.py
├── test_unlimited_characters.py
├── token_counter.py
├── ttrpg-config.json
├── update_app_embeddings.py
├── user_character_info.py
├── user_chat_history.py
├── verify_layout_fix.py
├── verify_optimization.py
└── verify_ttrpg_prompts.py
