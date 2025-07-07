#!/usr/bin/env python3
"""
futurehouse_stats.py – generate per-file statistics for FutureHouse dumps
"""

import json, csv, sys
from pathlib import Path
from collections import Counter

# ─────────────────────────── configuration ────────────────────────────
INPUT_JSON   = Path('futurehouse/all_responses_retry.json')   # full export
KINASES_CSV  = Path('data/kinases.csv')
OUTPUT_CSV   = Path('futurehouse/statistics.csv')
# ───────────────────────────────────────────────────────────────────────

PUB_TYPES = [
    "Review", "Study", "CaseReport", "LettersAndComments", "Editorial",
    "ClinicalTrial", "MetaAnalysis", "News", "Conference", "Dataset", "Book"
]

HEADERS = (
    ["uniprot", "protein",
     "candidate_contexts", "used_contexts", "DOIs", "cost",
     "sq0", "sq1", "sq2", "sq3"]
    + [f"type_{pt}" for pt in PUB_TYPES]
)

# ───────────────────────── helper functions ───────────────────────────
def load_uniprot_map(csv_path: Path) -> dict:
    with csv_path.open(newline='') as f:
        rdr = csv.DictReader(f)
        return {row["uniprot"].strip(): row["protein"].strip() for row in rdr}

def recurse(node):
    """Yield every dict in the JSON tree."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from recurse(v)
    elif isinstance(node, list):
        for item in node:
            yield from recurse(item)

def collect_pub_types(root) -> Counter:
    """Return Counter of publication types found anywhere under root."""
    counter = Counter()
    for d in recurse(root):
        if "publicationTypes" in d and isinstance(d["publicationTypes"], list):
            counter.update(pt.replace(' ', '') for pt in d["publicationTypes"])
        elif "publicationType" in d and isinstance(d["publicationType"], list):
            counter.update(pt.replace(' ', '') for pt in d["publicationType"])
    return counter

def collect_source_quality(root) -> Counter:
    counter = Counter()
    for d in recurse(root):
        sq = None
        if "source_quality" in d:
            sq = d["source_quality"]
        elif "metadata" in d and isinstance(d["metadata"], dict):
            sq = d["metadata"].get("source_quality")
        if sq in (0, 1, 2, 3):
            counter[sq] += 1
    return counter

# ─────────────────────────────── main ─────────────────────────────────
def main():
    if not INPUT_JSON.exists():
        sys.exit(f"Error: {INPUT_JSON} not found")

    up2prot = load_uniprot_map(KINASES_CSV)

    with INPUT_JSON.open() as f:
        data = json.load(f)

    rows = []

    for fname, entry in data.items():
        uniprot = fname.split('_')[0].split('.')[0]
        protein = up2prot.get(uniprot, '')

        ans = (entry.get('environment_frame', {})
                      .get('state', {})
                      .get('state', {})
                      .get('response', {})
                      .get('answer', {}))

        contexts      = ans.get('contexts', []) or []
        used_contexts = ans.get('used_contexts', []) or []

        dois = {ctx.get('text', {}).get('doc', {}).get('doi')
                for ctx in contexts if isinstance(ctx, dict)}
        dois.discard(None)

        # gather counts ------------------------------------------------
        pt_counts = collect_pub_types(ans)
        sq_counts = collect_source_quality(ans)

        row = {
            "uniprot": uniprot,
            "protein": protein,
            "candidate_contexts": len(contexts),
            "used_contexts": len(used_contexts),
            "DOIs": len(dois),
            "cost": round(ans.get('cost', 0.0), 2),
            "sq0": sq_counts[0],
            "sq1": sq_counts[1],
            "sq2": sq_counts[2],
            "sq3": sq_counts[3],
        }
        for pt in PUB_TYPES:
            row[f"type_{pt}"] = pt_counts[pt]

        rows.append(row)

    if not rows:
        sys.exit("No data to write.")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows → {OUTPUT_CSV}")

# ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
