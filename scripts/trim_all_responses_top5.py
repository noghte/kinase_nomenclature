import json

# Load the JSON file
with open('futurehouse/all_responses.json', 'r') as f:
    data = json.load(f)

# Only include the first 5 entries and trim top-level strings
trimmed_data = {}
for i, (key, value) in enumerate(data.items()):
    if i >= 5:
        break
    trimmed_entry = {}
    for subkey, subvalue in value.items():
        if isinstance(subvalue, str) and len(subvalue) > 200:
            trimmed_entry[subkey] = subvalue[:200] + "..."
        else:
            trimmed_entry[subkey] = subvalue
    trimmed_data[key] = trimmed_entry

# Save the result
output_path = 'futurehouse/all_responses_top5_trimmed.json'
with open(output_path, 'w') as f:
    json.dump(trimmed_data, f, indent=2)
