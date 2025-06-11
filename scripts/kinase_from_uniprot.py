import csv
import requests
import time
import os

input_file = './data/classification.csv'
output_file = './data/classification_enriched.csv'

api_url = 'https://rest.uniprot.org/uniprotkb/search'
fields = 'protein_name,gene_names,cc_function'
headers = {'Accept': 'application/json'}

# Read the original source CSV
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    source_rows = list(reader)
    fieldnames = reader.fieldnames

# Load existing enriched data if available
enriched_rows = {}
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            enriched_rows[row['uniprotid']] = row

# Enrich missing rows and preserve order
updated_rows = []
for row in source_rows:
    uniprot_id = row.get('uniprotid')
    if not uniprot_id:
        updated_rows.append(row)
        continue

    if uniprot_id in enriched_rows:
        updated_rows.append(enriched_rows[uniprot_id])
        continue

    # Enrich this row using UniProt API
    params = {
        'query': f'accession:{uniprot_id}',
        'fields': fields,
        'format': 'json'
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to retrieve data for {uniprot_id}")
            updated_rows.append(row)
            continue

        data = response.json()
        if not data.get('results'):
            print(f"No data found for {uniprot_id}")
            updated_rows.append(row)
            continue

        entry = data['results'][0]

        # Fill in enrichment fields
        row['protein_name'] = (
            entry.get('proteinDescription', {})
            .get('recommendedName', {})
            .get('fullName', {})
            .get('value', '')
        )

        gene_synonyms = []
        for gene in entry.get('genes', []):
            for syn in gene.get('synonyms', []):
                gene_synonyms.append(syn.get('value', ''))
        row['gene_synonyms'] = '; '.join(gene_synonyms)

        alt_names = []
        for alt in entry.get('proteinDescription', {}).get('alternativeNames', []):
            name = alt.get('fullName', {}).get('value')
            if name:
                alt_names.append(name)
        row['protein_alternative_names'] = '; '.join(alt_names)

        function_comment = ''
        for comment in entry.get('comments', []):
            if comment.get('commentType') == 'FUNCTION':
                texts = comment.get('texts', [])
                if texts:
                    function_comment = texts[0].get('value', '')
                    break
        if len(function_comment) > 500:
            function_comment = function_comment[:500] + '...'
        row['function'] = function_comment

        print(f"Enriched {uniprot_id}")
        time.sleep(0.5)

    except Exception as e:
        print(f"Error processing {uniprot_id}: {e}")

    updated_rows.append(row)

# Write final merged/enriched file
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)

print(f"Completed. Output written to: {output_file}")