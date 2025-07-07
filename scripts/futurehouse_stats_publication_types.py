#!/usr/bin/env python3
"""
Scan a FutureHouse-style JSON dump and list every publication type encountered.

Usage:
    python scan_pub_types.py [path/to/json]

If no path is given it defaults to the trimmed file you used before.
"""

import json
import sys
from collections import Counter
from pathlib import Path

# ---------- config ----------
DEFAULT_FILE = Path("futurehouse/all_responses_retry.json")
# ----------------------------

def walk_candidates(node):
    """Yield every dict that can contain publicationTypes."""
    if isinstance(node, dict):
        if "publicationTypes" in node:
            yield node
        else:
            for v in node.values():
                yield from walk_candidates(v)
    elif isinstance(node, list):
        for item in node:
            # unwrap {"call_xyz": {...}}
            if isinstance(item, dict) and len(item) == 1:
                inner = next(iter(item.values()))
                yield from walk_candidates(inner)
            else:
                yield from walk_candidates(item)

def main(path: Path):
    with path.open() as f:
        data = json.load(f)

    counter = Counter()

    for entry in data.values():
        answer = (entry.get("environment_frame", {})
                        .get("state", {})
                        .get("state", {})
                        .get("response", {})
                        .get("answer", {}))

        for cand in walk_candidates(answer.get("candidates", [])):
            for pt in (cand.get("publicationTypes") or []):
                if pt:                          # skip None / ''
                    counter[pt.strip()] += 1    # keep original spelling

    # -------- report --------
    if not counter:
        print("No publicationTypes found.")
        return

    print(f"Found {len(counter)} distinct publicationTypes:\n")
    for pt, cnt in counter.most_common():
        print(f"{pt:<20} {cnt}")

if __name__ == "__main__":
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    if not json_path.exists():
        sys.exit(f"Error: '{json_path}' not found")
    main(json_path)

# Output:
# Review               11556
# Study                929
# CaseReport           257
# LettersAndComments   237
# Editorial            111
# ClinicalTrial        81
# MetaAnalysis         69
# News                 31
# Conference           16
# Dataset              4
# Book                 2