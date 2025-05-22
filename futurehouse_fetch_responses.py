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
task_ids_file  = Path("./futurehouse/task_ids_20250522_121404.txt")
csv_file       = Path("./data/kinases.csv")
responses_file = Path("./futurehouse/responses.json")

# Load or initialize responses
if responses_file.exists():
    with open(responses_file, encoding="utf-8") as f:
        responses = json.load(f)
else:
    responses = {}

# Read task IDs
with open(task_ids_file, encoding="utf-8") as f:
    task_ids = [line.strip() for line in f if line.strip()]

# Read CSV rows
with open(csv_file, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for idx, tid in enumerate(task_ids):
    # skip only if we already have a non‐error result
    if tid in responses and "error" not in responses[tid]:
        continue

    # Poll until completion
    while True:
        status = client.get_task(tid)
        state  = status.status.lower()  # normalize to lowercase

        if state == "success":
            row = rows[idx]
            # Extract professor field (handle possible BOM)
            prof_key = next((k for k in row if k.strip().lower() == "professor"), None)

            # Build combined record
            record = {
                "uniprotid":  row.get("uniprotid", ""),
                "gene_name":  row.get("gene_name", ""),
                "professor":  row.get("\ufeffprofessor", ""),
                "successful": status.has_successful_answer,
                "answer":     status.formatted_answer,
                "reasoning":  getattr(status, "answer_reasoning", None),
            }

            # Save into responses and flush
            responses[tid] = record
            with open(responses_file, "w", encoding="utf-8") as out:
                json.dump(responses, out, indent=2, ensure_ascii=False)

            print(f"{tid} done")
            break

        if state in ("pending", "running"):
            time.sleep(5)
            continue

        # Terminal failure
        responses[tid] = {"task_id": tid, "error": state}
        with open(responses_file, "w", encoding="utf-8") as out:
            json.dump(responses, out, indent=2, ensure_ascii=False)
        print(f"{tid} failed with state {state}")
        break

client.close()
print("Finished polling and updated responses.json")
