# 🎯 Demerzel Guidelines

**Flask TTRPG Chatbot - Windows 11 PC Only**

**Requirements:** Windows 11, Desktop 1920x1080+, Edge/Chrome/Firefox, Keyboard/mouse, PC-first, WCAG 2.1 AA

**Structure:** `/static/ttrpg-chatbot/` (main), `/static/<ttrpg>/` (modules), `/docs/`, `/scripts/`
**Code:** No duplicates/orphans, 1.0em+ fonts, PC padding, remove mobile CSS/touch/webkit

**Layout:** 3-col `250px 1fr 40%` (buttons|character|chat), 20 buttons 1.0em, dark theme #121212/#e0e0e0, Segoe UI 1.15em, hover states, 8px radius

**Commands:**

```bash
./start.sh ./deploy.sh ./backup.sh          # Dev, prod, backup
cp .env.example .env; nano .env              # FLASK_SECRET_KEY, OPENAI_API_KEY
python scripts/register_ttrpg.py register --name "x" --display-name "X"
python scripts/test_ttrpg_integration.py; ./deploy.sh
```

**Stack:** HTML5+ARIA, CSS3 grid, ES6 IIFE, Marked.js | Python 3.8+, Flask, OpenAI | Gunicorn single worker, env vars

**TTRPG:** `/static/<name>/system_prompt.txt` (required), optional: index.html, css/, js/
**Setup:** register → edit prompt → test → deploy
**Prompt:** `You are [GM] for [TTRPG]. Tone: [x]. Goals: [x]. Never break character.`
**Naming:** lowercase-hyphens, 20 button files button1-20.txt

**System Architecture:** Universal system_prompt.txt + TTRPG-specific system_prompt.txt = unique AI personality
**Active TTRPGs:** dune, mouse-guard, the-one-ring, zweihander, cyberpunk, pendragon, master-template
**Embeddings:** Supabase-hosted game manuals (env: SUPABASE_PROJECT_URL, SUPABASE_ANON_KEY, SUPABASE_BUCKET_NAME)
**Response Format:** TRIPARTITE_CHECK (3-stage actions), markdown formatting, 3-5 sentences max, always end with prompt

**Embedding Process:** text → 500-char chunks with 100-char overlap → OpenAI text-embedding-3-small → JSON → Supabase bucket
**Commands:** `python scripts/generate_embeddings.py` → `./scripts/upload_embeddings.sh` → auto-download via lockdown_embedding_loader.py
**File Format:** `embeddings/<ttrpg-name>.json` with {source, text, embedding} structure

**New TTRPG Process:**

1. `python scripts/register_ttrpg.py register --name "system-name" --display-name "Display Name" --gm-title "GM Title"`
2. Edit `static/system-name/system_prompt.txt` (created from template)
3. Add documents to `static/text/system-name/` (optional)
4. Generate embeddings: `python scripts/generate_embeddings.py` + `./scripts/upload_embeddings.sh` (optional)
5. Test: `python scripts/test_ttrpg_integration.py --ttrpg system-name`
6. Deploy: `./deploy.sh` (auto-registers routes from ttrpg-config.json)
7. Update PROJECT_GUIDELINES.md Active TTRPGs list

**QA:** Remove redundant code, update comments, test PC interface, validate accessibility
**Security:** Env vars, input validation, CSP headers | **Performance:** Single worker, cache, optimized delivery

**Guidelines Maintenance:** After any project changes, update PROJECT_GUIDELINES.md: add new TTRPGs to Active TTRPGs list, document new processes/systems for reuse, update commands/patterns, maintain single source of truth

**CRITICAL ADHERENCE PROTOCOLS:**
**Pre-Task:** ALWAYS read PROJECT_GUIDELINES.md first - contains ALL project standards, file structures, coding rules, UI specs, TTRPG integration, embedding processes
**During Task:** Reference guidelines for decisions on layout (3-col), colors (#121212/#e0e0e0), fonts (Segoe UI 1.15em), PC-only approach, no mobile code
**Post-Task:** Update guidelines with new patterns/systems for future consistency - this file IS the single source of truth for ALL development decisions

**Principle:** Windows 11 PC desktop only, no mobile support
