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

exclude_indices = set([76,77,89,109,110,112,113,152,153,182,185,242,243,246,265,266,267,269,270,306,307,309,310,312,314,316,317,318,322,323,324,325,398,410,411,426,466,467,468,469,499,503,504,506,508,509,510,511,519,520,521,523,538,539,540,541,544,545,579,580,581,582,684,713,714,746,747,756,781,828,237 ,238,239 ,240,244 ,245,247 ,248,249 ,250,254 ,255,256 ,257,424 ,425,501 ,502,519 ,522,774 ,775])

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

# after you set rows_to_submit based on choice
# e.g. rows_to_submit = reader  or the failed‐only subset

# filter out any row whose index value is in exclude_indices


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

# rows_to_submit = [
#     row for row in rows_to_submit
#     if int(row["index"]) not in exclude_indices
# ]

#temp
# rows_to_submit = [
#     row for row in rows_to_submit
#     if row.get("uniprot") == "O15075"
#     ]

print(f"Submitting {len(rows_to_submit)} tasks, writing to {out_path.name}")
confirm = input("Proceed? (y/n): ").strip().lower()
if confirm != "y":
    print("Cancelled by user.")
    client.close()
    exit(0)

# submit and write CSV
    # submit and write CSV
with open(out_path, "w", encoding="utf-8", newline="") as out:
    writer = csv.writer(out)
    writer.writerow(["protein", "task_id"])
    for row in rows_to_submit:
        prompt = template.format(
            protein_name              = row.get("protein_name", ""),
            gene_name                 = row.get("protein", ""),           
            gene_synonyms             = row.get("gene_synonyms", "N/A"),
            uniprotid                 = row.get("uniprot", ""),          
            protein_alternative_names = row.get("protein_alternative_names", "N/A"),
            function                  = row.get("function", "N/A")[:1000],
        )
        # write prompt to a text file for debugging
        prompt_file = Path(f"./futurehouse/prompts/{row['uniprot']}_prompt.txt")
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        with open(prompt_file, "w", encoding="utf-8") as pf:
            pf.write(prompt)
            print(f"Prompt written to {prompt_file}")

        # task = TaskRequest(
        #     name=job_name,
        #     query=prompt,
        # )

        # tid = client.create_task(task)
        # writer.writerow([row["protein"], tid])                     
        # print("Submitted", row["protein"], "→", tid)
        # time.sleep(0.1)


  
client.close()
print("Client closed successfully.")