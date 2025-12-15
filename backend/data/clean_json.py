import json

INPUT_FILE = "sensors_with_health.json"
OUTPUT_FILE = "sensors_without_health.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

def remove_health_index(obj):
    if isinstance(obj, dict):
        obj.pop("Health_Index", None)
        for v in obj.values():
            remove_health_index(v)
    elif isinstance(obj, list):
        for item in obj:
            remove_health_index(item)

remove_health_index(data)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("sensors_without_health.json created successfully")
