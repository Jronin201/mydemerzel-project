# 🎯 Demerzel Guidelines

**Flask TTRPG Chatbot - Windows 11 PC Only**

**Requirements:** Windows 11, Desktop 1920x1080+, Edge/Chrome/Firefox, Keyboard/mouse, PC-first, no mobile, WCAG 2.1 AA

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

**QA:** Remove redundant code, update comments, test PC interface, validate accessibility
**Security:** Env vars, input validation, CSP headers | **Performance:** Single worker, cache, optimized delivery

**Principle:** Windows 11 PC desktop only, no mobile support
