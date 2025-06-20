#!/usr/bin/env python3
import json
import os
import pypandoc

# Path to your JSON and outputs root
RESPONSES_JSON = "./futurehouse/responses_20250616_235156.json"
OUTPUT_ROOT    = "./futurehouse/outputs"

def sanitize_filename(name: str) -> str:
    """
    Remove any characters that are unsafe for filenames.
    """
    return "".join(c for c in name if c.isalnum() or c in " -_()").rstrip()

def main():
    # Load the JSON
    with open(RESPONSES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Make sure output folder exists
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    for uid, entry in data.items():
        # skip any failed tasks
        if "error" in entry:
            continue

        protein   = entry.get("protein")
        answer_md = entry.get("answer", "").strip()
        if not protein or not answer_md:
            # incomplete record or empty answer
            continue

        # If your old outputs still contain that template‐prefix, strip it
        marker = (
            "Strive for clarity, completeness, and adherence to the style and depth "
            "of the reference template"
        )
        if marker in answer_md:
            answer_md = answer_md.split(marker, 1)[1].lstrip("\n")

        fname = sanitize_filename(protein)
        docx_path = os.path.join(OUTPUT_ROOT, f"{fname}.docx")
        txt_path  = os.path.join(OUTPUT_ROOT, f"{fname}.txt")

        if os.path.exists(docx_path):
            print(f"✖ {docx_path} already exists, skipping.")
            continue

        try:
            # 1) convert markdown → docx
            pypandoc.convert_text(
                answer_md,
                to="docx",
                format="md",
                outputfile=docx_path
            )
            print(f"✔ Saved DOCX {docx_path}")

            # 2) write out the raw markdown as .txt
            with open(txt_path, "w", encoding="utf-8") as t:
                t.write(answer_md)
            print(f"✔ Saved TXT  {txt_path}")

        except Exception as e:
            print(f"✖ Failed to convert {uid} ({protein}): {e}")

if __name__ == "__main__":
    main()
