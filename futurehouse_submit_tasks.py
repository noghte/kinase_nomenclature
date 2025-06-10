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
API_KEY = os.getenv("FUTUREHOUSE_API_KEY")
if not API_KEY:
    raise RuntimeError("FUTUREHOUSE_API_KEY missing")

client    = FutureHouseClient(api_key=API_KEY)
csv_path  = Path("./data/kinases.csv")
tmpl_path = Path("./futurehouse/unified_prompt.txt")
template  = tmpl_path.read_text(encoding="utf-8")
job_name  = JobNames.FALCON  # or OWL / CROW

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
    print("To Submit:", [r["gene_name"] for r in rows_to_submit])
else:
    print("Invalid choice.")
    client.close()
    exit(1)

# prepare output file with timestamp
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out_path = Path(f"./futurehouse/task_ids_{ts}.csv")

print(f"Submitting {len(rows_to_submit)} tasks, writing to {out_path.name}")
confirm = input("Proceed? (y/n): ").strip().lower()
if confirm != "y":
    print("Cancelled by user.")
    client.close()
    exit(0)

# submit and write CSV
with open(out_path, "w", encoding="utf-8", newline="") as out:
    writer = csv.writer(out)
    writer.writerow(["gene_name", "task_id"])
    for row in rows_to_submit:
        prompt = template.format(
            protein_name              = row.get("protein_name", ""),
            gene_name                 = row.get("gene_name", ""),
            gene_synonyms             = row.get("gene_synonyms", "N/A"),
            uniprotid                 = row.get("uniprotid", ""),
            protein_alternative_names = row.get("protein_alternative_names", "N/A"),
            function                  = row.get("function", "N/A")
        )

        # Add general PDF documents
        pdf_dir = Path("./pdf/")
        docs = []
        if pdf_dir.exists() and pdf_dir.is_dir():
            for pdf in pdf_dir.glob("*.pdf"):
                docs.append({"path": str(pdf)})

        # Add gene-specific PDF documents if available
        pdf_dir = Path("./pdf") / row["gene_name"]
        if pdf_dir.exists() and pdf_dir.is_dir():
            for pdf in pdf_dir.glob("*.pdf"):
                docs.append({"path": str(pdf)})

        task = TaskRequest(
            name=job_name,
            query=prompt,
            runtime_config={"docs": docs} if docs else None
        )

        tid = client.create_task(task)
        writer.writerow([row["gene_name"], tid])
        print("Submitted", row["gene_name"], "→", tid)
        time.sleep(0.1)

client.close()
print("Client closed successfully.")