import json
import re

# Input and output file paths
input_file_path = './futurehouse/responses_20250601_231801.json'
output_file_path = './futurehouse/regulation_sections.json'

# Load the JSON file
with open(input_file_path, 'r', encoding='utf-8') as infile:
    data = json.load(infile)

# Pattern to extract Regulation section
pattern = r"\n\n6\. Regulation  \n(.*?)\n\n7\. Function  \n"
# pattern = r"\n\n(?:##\s*)?6\. Regulation\s{2}\n(.*?)\n\n(?:##\s*)?7\. Function\s{2}\n"
# Extracted data container
regulation_sections = {}

# Iterate and extract
for key, entry in data.items():
    answer = entry.get("answer", "")
    match = re.search(pattern, answer, re.DOTALL)
    if match:
        regulation_text = match.group(1).strip()
        gene_name = entry.get("gene_name", "Unknown Gene")
        regulation_sections[gene_name] = {
            "uniprotid": entry.get("uniprotid"),
            "gene_name": gene_name,
            "regulation": regulation_text
        }
    else:
        print(f"No regulation section found for {key}")
# Save the extracted sections
with open(output_file_path, 'w', encoding='utf-8') as outfile:
    json.dump(regulation_sections, outfile, indent=2, ensure_ascii=False)