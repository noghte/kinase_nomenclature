#!/usr/bin/env python3
import json
import os
import sys
import pypandoc

# Path to your JSON and outputs root
RESPONSES_JSON = "./futurehouse/responses.json"
OUTPUT_ROOT    = "./futurehouse/outputs"

def main():
    # Load the JSON
    with open(RESPONSES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    for uid, entry in data.items():
        prof     = entry.get("professor")
        gene     = entry.get("gene_name")
        answer_md= entry.get("answer", "")
        if answer_md == '':
            continue
        # We don't need the prompt part
        answer_md = answer_md.split("Strive for clarity, completeness, and adherence to the style and depth of the reference template\n\n")[1]

        if not prof or not gene or not answer_md:
            # skip incomplete entries
            continue

        # ensure per-professor directory exists
        prof_dir = os.path.join(OUTPUT_ROOT, prof)
        os.makedirs(prof_dir, exist_ok=True)

        # output filename
        out_path = os.path.join(prof_dir, f"{gene}.docx")

        # convert markdown to docx
        try:
            pypandoc.convert_text(
                answer_md,
                to="docx",
                format="md",
                outputfile=out_path
            )
            print(f"✔ Saved {out_path}")
        except Exception as e:
            print(f"✖ Failed to convert {uid} ({prof}/{gene}): {e}")

if __name__ == "__main__":
    main()
