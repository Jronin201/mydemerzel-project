#!/usr/bin/env python3
"""Quick validation of quick-insert button random line selection logic.

Replicates the front-end algorithm:
- Line 1 is the label (ignored for payload)
- Start considering lines from index 2 (file line 3) onward
- Collect non-empty trimmed lines only
- If none, fallback to concatenated text of lines[2:] or full trimmed file
- Random pick should always be one of candidate lines and never empty / label

Outputs a summary per button file and reports any anomalies.
"""
from pathlib import Path
import random
import hashlib
import json

BASE = Path('static')
SYSTEMS = [p for p in BASE.iterdir() if p.is_dir() and (p / 'button-texts').exists()]

def derive_candidates(text: str):
    lines = text.splitlines()
    line1 = (lines[0].strip() if lines else '')
    tail = [l.strip() for l in lines[2:]]  # from file line 3 onward
    candidates = [l for l in tail if l]
    if not candidates:
        fallback = ' '.join(lines[2:]).strip() or text.strip()
        candidates = [fallback]
    return line1, candidates

def main():
    report = []
    failures = 0
    for system in SYSTEMS:
        bt_dir = system / 'button-texts'
        for btn in sorted(bt_dir.glob('button*.txt')):
            text = btn.read_text(encoding='utf-8', errors='ignore')
            label, candidates = derive_candidates(text)
            # simulate 5 random picks
            picks = [random.choice(candidates) for _ in range(5)]
            bad = [p for p in picks if not p or p == label]
            entropy = len(set(picks))
            report.append({
                'system': system.name,
                'button': btn.name,
                'label': label,
                'candidate_count': len(candidates),
                'sample_picks': picks,
                'unique_in_samples': entropy,
                'hash_first_candidate': hashlib.md5(candidates[0].encode()).hexdigest() if candidates else None,
                'issue': 'label_in_picks' if bad else ''
            })
            if bad:
                failures += 1
    summary = {
        'systems_scanned': len(SYSTEMS),
        'files_scanned': len(report),
        'failures': failures,
    }
    print(json.dumps({'summary': summary, 'details': report[:10]}, indent=2))  # show only first 10 detail entries for brevity
    if failures:
        print(f"FAILURES detected: {failures}")
        return 1
    print("All sampled random picks valid (no label or empty lines).")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
