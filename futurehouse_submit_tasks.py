import os
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from futurehouse_client import FutureHouseClient, JobNames

load_dotenv()
API_KEY = os.getenv("FUTUREHOUSE_API_KEY")
if not API_KEY:
    raise RuntimeError("FUTUREHOUSE_API_KEY missing")

client   = FutureHouseClient(api_key=API_KEY)
csv_path = Path("./data/kinases.csv")
tmpl_path = Path("./futurehouse/unified_prompt.txt")
template = tmpl_path.read_text(encoding="utf-8")
job_name = JobNames.FALCON  # or OWL / CROW

# load existing responses to detect successes
resp_path = Path("./futurehouse/responses.json")
if resp_path.exists():
    with open(resp_path, encoding="utf-8") as f:
        all_responses = json.load(f)
else:
    all_responses = {}

successful_genes = {
    v["gene_name"] for v in all_responses.values() if "gene_name" in v
}

# menu
print("Options:")
print(f"1. Process all kinases from {csv_path.name}")
print("2. Process failed responses from ./futurehouse/responses.json")
print("3. Exit")
choice = input("Select option (1/2/3): ").strip()

if choice == "3":
    print("Exiting.")
    client.close()
    exit(0)

# determine which rows to submit
with open(csv_path, encoding="utf-8") as f:
    reader = list(csv.DictReader(f))

if choice == "1":
    rows_to_submit = reader
elif choice == "2":
    rows_to_submit = [r for r in reader if r["gene_name"] not in successful_genes]
    print("To Submit: ", rows_to_submit)
else:
    print("Invalid choice. Exiting.")
    client.close()
    exit(1)

# prepare output file with timestamp
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_path = Path(f"./futurehouse/task_ids_{ts}.txt")

print(f"Submitting {len(rows_to_submit)} tasks, writing IDs to {out_path.name}")
confirm = input("Proceed? (y/n): ").strip().lower()
if confirm != "y":
    print("Cancelled by user.")
    client.close()
    exit(0)

# submit
try:
    with open(out_path, "w", encoding="utf-8") as out:
        for row in rows_to_submit:
            prompt = template.format(
                protein_name=row.get("protein_name",""),
                gene_name=row.get("gene_name",""),
                gene_synonyms=row.get("gene_synonyms","N/A"),
                uniprotid=row.get("uniprotid",""),
                protein_alternative_names=row.get("protein_alternative_names","N/A"),
                function=row.get("function","N/A")
            )
            tid = client.create_task({"name": job_name, "query": prompt})
            out.write(f"{tid}\n")
            print("Submitted", tid)
            time.sleep(0.1)  # small pause to avoid rate limits
finally:
    client.close()
    print("Client closed successfully.")
