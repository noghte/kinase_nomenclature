import os
import time
import json
import csv
from pathlib import Path
from dotenv import load_dotenv
from futurehouse_client import FutureHouseClient

load_dotenv()
API_KEY = os.getenv("FUTUREHOUSE_API_KEY")
if not API_KEY:
    raise RuntimeError("FUTUREHOUSE_API_KEY missing")

client = FutureHouseClient(api_key=API_KEY)

# Paths
task_ids_file  = Path("./futurehouse/task_ids_all.csv")
csv_file       = Path("./data/kinases.csv")
responses_file = Path("./futurehouse/responses.json")

# Load or initialize responses
if responses_file.exists():
    with open(responses_file, encoding="utf-8") as f:
        responses = json.load(f)
else:
    responses = {}

# Read task‐to‐gene mapping
with open(task_ids_file, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    task_to_gene = { row["task_id"]: row["gene_name"] for row in reader }

task_ids = list(task_to_gene.keys())

# Read CSV rows
with open(csv_file, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    all_rows    = list(reader)
    row_by_gene = { row["gene_name"]: row for row in all_rows }

for tid in task_ids:
    # skip only if we already have a non-error result
    if tid in responses and "error" not in responses[tid]:
        continue

    status = client.get_task(tid)
    state  = status.status.lower()

    if state == "success":
        gene = task_to_gene[tid]
        row  = row_by_gene.get(gene)
        if row is None:
            raise RuntimeError(f"No CSV row for gene {gene!r}, task {tid}")

        record = {
            "uniprotid":  row.get("uniprotid", ""),
            "gene_name":  gene,
            "professor":  row.get("\ufeffprofessor", ""),
            "successful": status.has_successful_answer,
            "answer":     status.formatted_answer,
            "reasoning":  getattr(status, "answer_reasoning", None),
        }
        responses[tid] = record
        with open(responses_file, "w", encoding="utf-8") as out:
            json.dump(responses, out, indent=2, ensure_ascii=False)

        print(f"{tid} done for gene {gene}")

    elif state in ("pending", "running", "in progress"):
        print(f"{tid} is still '{state}', skipping for now.")
        continue

    else:
        # terminal failure
        responses[tid] = {"task_id": tid, "error": state}
        with open(responses_file, "w", encoding="utf-8") as out:
            json.dump(responses, out, indent=2, ensure_ascii=False)
        print(f"{tid} failed with state {state}")

client.close()
print("Finished polling and updated responses.json")
