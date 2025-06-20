import os
import json
import csv
from pathlib import Path
from dotenv import load_dotenv
from futurehouse_client import FutureHouseClient

load_dotenv()
API_KEY = os.getenv("FUTUREHOUSE_API_KEY")
if not API_KEY:
    raise RuntimeError("FUTUREHOUSE_API_KEY missing")

# change this prefix to match your files in futurehouse/
PREFIX = "task_ids_20250616_"
TASKS_DIR      = Path("./futurehouse")
CSV_FILE       = Path("./data/kinases.csv")
RESPONSES_FILE = TASKS_DIR / "responses_20250616_235156.json"

client = FutureHouseClient(api_key=API_KEY)

# load or initialize existing responses
if RESPONSES_FILE.exists():
    with open(RESPONSES_FILE, encoding="utf-8") as f:
        responses = json.load(f)
else:
    responses = {}

# collect task_id → protein from all matching CSVs (original + retries)
task_to_protein = {}
for csv_path in TASKS_DIR.glob(f"*{PREFIX}*.csv"):
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            task_to_protein[row["task_id"]] = row["protein"]

task_ids = list(task_to_protein.keys())

# load the master kinases.csv so we can look up uniprot etc
with open(CSV_FILE, encoding="utf-8") as f:
    reader         = csv.DictReader(f)
    all_rows       = list(reader)
    row_by_protein = { row["protein"]: row for row in all_rows }

# poll every task
for tid in task_ids:
    # skip if already have a non-error result
    if tid in responses and "error" not in responses[tid]:
        continue

    status = client.get_task(tid)
    state  = status.status.lower()

    if state == "success":
        protein = task_to_protein[tid]
        row     = row_by_protein.get(protein)
        if row is None:
            raise RuntimeError(f"No CSV row for protein {protein!r}, task {tid}")

        record = {
            "uniprot":    row.get("uniprot", ""),
            "protein":    protein,
            "successful": status.has_successful_answer,
            "answer":     status.formatted_answer,
            "reasoning":  getattr(status, "answer_reasoning", None),
        }
        responses[tid] = record
        with open(RESPONSES_FILE, "w", encoding="utf-8") as out:
            json.dump(responses, out, indent=2, ensure_ascii=False)

        print(f"{tid} done for protein {protein}")

    elif state in ("pending", "running", "in progress"):
        print(f"{tid} is still '{state}', skipping for now")

    else:
        # terminal failure
        responses[tid] = {"task_id": tid, "error": state}
        with open(RESPONSES_FILE, "w", encoding="utf-8") as out:
            json.dump(responses, out, indent=2, ensure_ascii=False)

        print(f"{tid} failed with state {state}")

client.close()
print(f"Finished polling and updated {RESPONSES_FILE}")
