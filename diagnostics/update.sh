#!/bin/bash

echo "[+] Gathering project diagnostics..."

mkdir -p diagnostics
bash -c 'tree -a -L 3' > diagnostics/tree.txt
pip freeze > diagnostics/pip.txt
find . -name "*.py" | xargs wc -l > diagnostics/py_lines.txt
find . -type f \( -name "*.html" -o -name "*.js" -o -name "*.css" \) > diagnostics/frontend_files.txt
[ -f .env ] && cat .env > diagnostics/env.txt || echo "# .env not found" > diagnostics/env.txt
git status > diagnostics/git.txt
code --list-extensions > diagnostics/extensions.txt
python --version > diagnostics/python_version.txt

echo "[✓] Diagnostics updated in /diagnostics"

# Combine all diagnostics into a single file for easy copy/paste
COMBINED=diagnostics/combined.txt
echo "[+] Creating combined diagnostics file..."
{
  echo "===== TREE ====="
  cat diagnostics/tree.txt
  echo

  echo "===== PIP FREEZE ====="
  cat diagnostics/pip.txt
  echo

  echo "===== PYTHON LINE COUNT ====="
  cat diagnostics/py_lines.txt
  echo

  echo "===== FRONTEND FILES ====="
  cat diagnostics/frontend_files.txt
  echo

  echo "===== .ENV ====="
  [ -f .env ] && cat diagnostics/env.txt || echo "No .env file found."
  echo

  echo "===== GIT STATUS ====="
  cat diagnostics/git.txt
  echo

  echo "===== EXTENSIONS ====="
  cat diagnostics/extensions.txt
  echo

  echo "===== PYTHON VERSION ====="
  cat diagnostics/python_version.txt
  echo

} > "$COMBINED"

echo "[✓] Combined diagnostics saved to diagnostics/combined.txt"
