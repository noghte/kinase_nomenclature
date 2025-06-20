import os
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models.app import TaskRequest

load_dotenv()
API_KEY = os.getenv('FUTUREHOUSE_API_KEY')
if not API_KEY:
    raise RuntimeError('FUTUREHOUSE_API_KEY missing')

client     = FutureHouseClient(api_key=API_KEY)
csv_path   = Path('./data/kinases.csv')
tmpl_path  = Path('./futurehouse/unified_prompt.txt')
template   = tmpl_path.read_text(encoding='utf-8')
job_name   = JobNames.FALCON

# original mapping and responses
task_ids_file  = Path('./futurehouse/task_ids_20250616_235156.csv')
responses_file = Path('./futurehouse/responses_20250616_235156.json')
out_path = Path('./futurehouse/task_ids_20250616_235156_retries.csv')

with open(responses_file, encoding='utf-8') as f:
    responses = json.load(f)

with open(task_ids_file, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    task_to_protein = {row['task_id']: row['protein'] for row in reader}

with open(csv_path, encoding='utf-8') as f:
    reader          = csv.DictReader(f)
    row_by_protein  = {row['protein']: row for row in reader}

# find all failed task IDs
failed = [tid for tid, rec in responses.items() if 'error' in rec]
print(f'{len(failed)} failed tasks to retry')

with open(out_path, 'w', newline='', encoding='utf-8') as out:
    writer = csv.writer(out)
    writer.writerow(['protein', 'task_id'])

    for old_tid in failed:
        protein = task_to_protein.get(old_tid)
        row     = row_by_protein[protein]

        prompt = template.format(
            protein_name              = row.get('protein_name', ''),
            gene_name                 = row.get('protein', ''),
            gene_synonyms             = row.get('gene_synonyms', 'N/A'),
            uniprotid                 = row.get('uniprot', ''),
            protein_alternative_names = row.get('protein_alternative_names', 'N/A'),
            function                  = row.get('function', 'N/A')[:1000],
        )

        task    = TaskRequest(name=job_name, query=prompt)
        new_tid = client.create_task(task)

        writer.writerow([protein, new_tid])
        print('Resubmitted', protein, '→', new_tid)
        time.sleep(0.1)

client.close()
print(f'Wrote retries to {out_path}')
