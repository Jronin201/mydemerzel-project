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
