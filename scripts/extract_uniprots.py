import os
import json
import time
import requests
import pandas as pd

# Paths
XLSX_PATH = './data/Kinases_Kannan_updated.xlsx'
JSON_OUTPUT_PATH = './data/gene_to_uniprot.json'

# Sheet name and column
SHEET_NAME = 'Updated Data'
GENE_COL = 'Gene Names (human)'

# UniProt search base URL
UNIPROT_SEARCH_BASE = 'https://rest.uniprot.org/uniprotkb/search'

def query_uniprot_for_gene(gene_symbol):
    """
    Query UniProt for the given human gene symbol.
    Returns a list of UniProt accessions (may be empty).
    """
    params = {
        'query': f'gene_exact:{gene_symbol} AND organism_id:9606',
        'fields': 'accession',
        'format': 'json',
        'limit': 10  # adjust if expecting more hits
    }
    try:
        resp = requests.get(UNIPROT_SEARCH_BASE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get('results', [])
        return [entry.get('primaryAccession') for entry in results if entry.get('primaryAccession')]
    except Exception as e:
        print(f"Warning: UniProt query failed for {gene_symbol}: {e}")
        return []

def main():
    # Load Excel into pandas DataFrame
    df = pd.read_excel(
        XLSX_PATH,
        sheet_name=SHEET_NAME,
        usecols=[GENE_COL]
    )

    entries = []
    token_cache = {}
    seen_values = set()

    for raw_value in df[GENE_COL].dropna():
        value = str(raw_value).strip()
        if not value or value in seen_values:
            continue
        seen_values.add(value)

        tokens = [tok.strip() for tok in value.split(',') if tok.strip()]
        all_uniprot_ids = set()

        for tok in tokens:
            if tok in token_cache:
                ids = token_cache[tok]
            else:
                ids = query_uniprot_for_gene(tok)
                token_cache[tok] = ids
                time.sleep(0.2)
            if ids:
                all_uniprot_ids.update(ids)

        if all_uniprot_ids:
            entries.append({
                "value": value,
                "uniprotids": sorted(all_uniprot_ids)
            })

    # Save to JSON
    os.makedirs(os.path.dirname(JSON_OUTPUT_PATH), exist_ok=True)
    with open(JSON_OUTPUT_PATH, 'w') as f:
        json.dump(entries, f, indent=2)

    print(f"Generated JSON with {len(entries)} entries: {JSON_OUTPUT_PATH}")


if __name__ == '__main__':
    main()