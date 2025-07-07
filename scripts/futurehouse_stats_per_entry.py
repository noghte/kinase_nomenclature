#!/usr/bin/env python3
import json, csv, sys
from pathlib import Path

# ----------------------------------------------------------------------
INPUT_JSON   = Path('futurehouse/all_responses_retry.json')
KINASES_CSV  = Path('data/kinases.csv')
OUTPUT_CSV   = Path('futurehouse/statistics.csv')

# publication-type columns you already asked for
PUB_TYPES = [
    "Review", "Study", "CaseReport", "LettersAndComments", "Editorial",
    "ClinicalTrial", "MetaAnalysis", "News", "Conference", "Dataset", "Book"
]

HEADERS = (
    ["uniprot", "protein",                 # <- new columns
     "candidate_contexts", "used_contexts", "DOIs", "cost",
     "sq0", "sq1", "sq2", "sq3"] +
    [f"type_{pt}" for pt in PUB_TYPES]
)

# ----------------------------------------------------------------------
def load_uniprot_map(csv_path: Path) -> dict:
    """Return {uniprot -> protein} from kinases.csv."""
    with csv_path.open(newline='') as f:
        rdr = csv.DictReader(f)
        return {row["uniprot"].strip(): row["protein"].strip() for row in rdr}

def walk_candidates(node):
    if isinstance(node, dict):
        if 'publicationTypes' in node or 'source_quality' in node:
            yield node
        else:
            for v in node.values(): yield from walk_candidates(v)
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and len(item) == 1:     # {"call_*": {...}}
                yield from walk_candidates(next(iter(item.values())))
            else:
                yield from walk_candidates(item)

# ----------------------------------------------------------------------
def main():
    up2prot = load_uniprot_map(KINASES_CSV)

    with INPUT_JSON.open() as f:
        data = json.load(f)

    rows = []

    for key, entry in data.items():
        uniprot = key.split('_')[0].split('.')[0]          # e.g. P31749_prompt.txt → P31749
        protein = up2prot.get(uniprot, '')                 # blank if not found

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

        sq = {0:0, 1:0, 2:0, 3:0}
        pt = {p:0 for p in PUB_TYPES}

        for cand in walk_candidates(ans.get('candidates', [])):
            if cand.get('source_quality') in sq: sq[cand['source_quality']] += 1
            for p in (cand.get('publicationTypes') or []):
                key2 = p.replace(' ', '')
                if key2 in pt: pt[key2] += 1

        row = {
            "uniprot": uniprot,
            "protein": protein,
            "candidate_contexts": len(contexts),
            "used_contexts": len(used_contexts),
            "DOIs": len(dois),
            "cost": round(ans.get('cost', 0.0), 2),
            "sq0": sq[0], "sq1": sq[1], "sq2": sq[2], "sq3": sq[3],
        }
        for p in PUB_TYPES:
            row[f"type_{p}"] = pt[p]

        rows.append(row)

    if not rows:
        sys.exit("No data to write.")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows → {OUTPUT_CSV}")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
