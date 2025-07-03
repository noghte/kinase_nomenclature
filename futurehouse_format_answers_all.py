#!/usr/bin/env python3
import json
import os
import pypandoc
import re
# Path to your JSON and outputs root
RESPONSES_JSON = "./futurehouse/all_responses_retry.json"
OUTPUT_ROOT    = "./futurehouse/outputs_v4"

def sanitize_filename(name: str) -> str:
    """
    Remove any characters that are unsafe for filenames.
    """
    nospace_name = name.replace(" ", "_")
    return "".join(c for c in nospace_name if c.isalnum() or c in " -_()").rstrip()

def main():
    # Load the JSON
    with open(RESPONSES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Make sure output folder exists
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    for uid, entry in data.items():
        # skip any failed tasks
        if entry.get("status") != "success":
            print(f"✖ Skipping due to error or incomplete status: {uid}")
            continue
        
        match = re.search(r'gene:\s*(.+?)(?=\*|$|\n)',entry["task"])
        protein = uid.split("_")[0]
        if match:
            protein = protein + "_" + match.group(1).strip()
        answer_md = ""
        answer_entry = entry['environment_frame']['state']['state']['response']['answer']
        if answer_entry['has_successful_answer']:
            answer_md = answer_entry['formatted_answer']
            references = answer_entry.get('references', "")
            if not references:
                print(f"✖ No references for {uid} ({protein}), skipping.")
                continue
            contexts = answer_entry.get('contexts', [])
            used_contexts = answer_entry.get('used_contexts', [])
            if len(contexts) == 0 or len(used_contexts) == 0:
                print(f"✖ No contexts or used contexts for {uid} ({protein}), skipping.")
                continue
        else:
            # print(f"✖ No successful answer for {uid} ({protein}), skipping.")
            continue
        # If your old outputs still contain that template‐prefix, strip it
        marker = (
            "Do not include theses or articles with unknown journal\n\n"
        )
        if marker in answer_md:
            answer_md = answer_md.split(marker, 1)[1].lstrip("\n")
        else:
            print(f"✖ No marker found in {uid} ({protein}), skipping.")

        fname = sanitize_filename(protein)
        docx_path = os.path.join(OUTPUT_ROOT, f"{fname}.docx")
        txt_path  = os.path.join(OUTPUT_ROOT, f"{fname}.txt")

        # if the new file size is larger than the existing one, overwrite it
        if os.path.exists(txt_path) and os.path.getsize(txt_path) > 0:
            existing_size = os.path.getsize(docx_path)
            new_size = len(answer_md.encode('utf-8'))
            if new_size > existing_size:
                print(f"✔ Overwriting {docx_path} with larger file.")
            else:
                # print(f"✖ {docx_path} already exists and is larger, skipping.")
                continue

        #fixing answer_md so it is not interpreted as a YAML file
        answer_md = answer_md.replace("---\n", "\n").replace("\n---", "\n")
        try:
            # 1) convert markdown → docx
            pypandoc.convert_text(
                answer_md,
                to="docx",
                format="md",
                outputfile=docx_path
            )
            # print(f"✔ Saved DOCX {docx_path}")

            # 2) write out the raw markdown as .txt
            with open(txt_path, "w", encoding="utf-8") as t:
                t.write(answer_md)
            # print(f"✔ Saved TXT  {txt_path}")

        except Exception as e:
            print(f"✖ Failed to convert {uid} ({protein}): {e}")

if __name__ == "__main__":
    main()
