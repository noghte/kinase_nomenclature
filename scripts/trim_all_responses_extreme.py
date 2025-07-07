import json

def trim_value(value):
    if isinstance(value, str):
        return value[:200] + "..." if len(value) > 200 else value
    elif isinstance(value, list):
        return [trim_value(v) for v in value[:3]] + (["..."] if len(value) > 3 else [])
    elif isinstance(value, dict):
        return {k: trim_value(v) for k, v in value.items()}
    else:
        return value

# Load the JSON file
with open('futurehouse/all_responses.json', 'r') as f:
    data = json.load(f)

# Process the first 3 entries
trimmed_data = {}
for i, (key, value) in enumerate(data.items()):
    if i >= 3:
        break
    trimmed_data[key] = trim_value(value)

# Save to file
output_path = 'futurehouse/all_responses_trimmed.json'
with open(output_path, 'w') as f:
    json.dump(trimmed_data, f, indent=2)
