#!/usr/bin/env python3
"""
scan_fh_json.py – quick statistics for FutureHouse result dumps

Stats reported
--------------
• # of entries (files) scanned
• # of candidate objects inspected
• total & unique DOIs
• publicationTypes     – frequency table
• source_quality (0/1/2/3) – frequency table
• contexts per entry   – min / mean / median / max
• used_contexts per entry – min / mean / median / max

Usage
-----
python scan_fh_json.py path/to/all_responses.json
If no path is supplied the script falls back to
'futurehouse/all_responses_top5_trimmed.json'.
"""

import json, sys, statistics
from pathlib import Path
from collections import Counter, defaultdict

DEFAULT_FILE = Path('futurehouse/all_responses_retry.json')

# ----------------------------------------------------------------------
def walk_candidates(node):
    """Yield each dict that may contain publicationTypes / source_quality."""
    if isinstance(node, dict):
        if 'publicationTypes' in node or 'source_quality' in node:
            yield node
        else:
            for v in node.values():
                yield from walk_candidates(v)
    elif isinstance(node, list):
        for item in node:
            # unwrap {"call_xyz": {...}}
            if isinstance(item, dict) and len(item) == 1:
                yield from walk_candidates(next(iter(item.values())))
            else:
                yield from walk_candidates(item)

# ----------------------------------------------------------------------
def median_or_zero(seq):
    return statistics.median(seq) if seq else 0

def mean_or_zero(seq):
    return sum(seq) / len(seq) if seq else 0

# ----------------------------------------------------------------------
def main(path: Path):
    with path.open() as f:
        data = json.load(f)

    pub_counter   = Counter()
    qual_counter  = Counter()
    unique_dois   = set()
    ctx_lengths   = []
    used_ctx_lens = []
    candidate_total = 0

    for entry in data.values():
        ans = (entry.get('environment_frame', {})
                    .get('state', {})
                    .get('state', {})
                    .get('response', {})
                    .get('answer', {}))

        # per-entry lists ----------------------------------------------
        contexts = ans.get('contexts', []) or []
        used_ctx = ans.get('used_contexts', []) or []

        ctx_lengths.append(len(contexts))
        used_ctx_lens.append(len(used_ctx))

        # collect DOIs present in contexts -----------------------------
        for c in contexts:
            doi = c.get('text', {}).get('doc', {}).get('doi')
            if doi:
                unique_dois.add(doi)

        # walk every candidate object ----------------------------------
        for cand in walk_candidates(ans.get('candidates', [])):
            candidate_total += 1

            for pt in cand.get('publicationTypes') or []:
                if pt:
                    pub_counter[pt.strip()] += 1

            sq = cand.get('source_quality')
            if sq in (0, 1, 2, 3):
                qual_counter[sq] += 1

    # ------------------  report  --------------------------------------
    print('=' * 60)
    print(f'Entries scanned         : {len(data):>6}')
    print(f'Candidate objects       : {candidate_total:>6}')
    print(f'Total DOIs referenced   : {len(unique_dois):>6}')
    print()


    print('Source quality counts:')
    for sq in (0, 1, 2, 3):
        print(f'  quality {sq}: {qual_counter[sq]}')
    print()


    if ctx_lengths:
        print('Contexts list length:')
        print(f'  min / mean / median / max : '
              f'{min(ctx_lengths)} / {mean_or_zero(ctx_lengths):.2f} / '
              f'{median_or_zero(ctx_lengths)} / {max(ctx_lengths)}')
    if used_ctx_lens:
        print('Used contexts length:')
        print(f'  min / mean / median / max : '
              f'{min(used_ctx_lens)} / {mean_or_zero(used_ctx_lens):.2f} / '
              f'{median_or_zero(used_ctx_lens)} / {max(used_ctx_lens)}')
    print('=' * 60)

# ----------------------------------------------------------------------
if __name__ == '__main__':
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    if not json_path.exists():
        sys.exit(f'Error: {json_path} not found')
    main(json_path)

# Output:
# Entries scanned         :    540
# Candidate objects       :  48326
# Total DOIs referenced   :   4875

# Source quality counts:
#   quality 0: 1361
#   quality 1: 15926
#   quality 2: 7445
#   quality 3: 7905

# Contexts list length:
#   min / mean / median / max : 25 / 67.79 / 57.0 / 267
# Used contexts length:
#   min / mean / median / max : 0 / 20.91 / 20.0 / 60