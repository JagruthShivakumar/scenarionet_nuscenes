import csv
import json

# === Paths ===
CSV_PATH = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output_tags/scene-0553_actor_dynamics.csv"
TAGS_JSON_PATH = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output_tags/scene-0553_activity_tags.json"
OUT_PATH = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output_tags/scene-0553_actor_dynamics_tagged.csv"

# === Load activity tags ===
with open(TAGS_JSON_PATH, "r") as f:
    tags = json.load(f)

# === Process and merge ===
with open(CSV_PATH, "r") as infile, open(OUT_PATH, "w", newline="") as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["longitudinal", "lateral"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        actor_id = row["actor_id"]
        frame = int(row["frame"])

        # Default tags if missing
        long_tag = tags.get(actor_id, {}).get("longitudinal", [])
        lat_tag = tags.get(actor_id, {}).get("lateral", [])
        
        row["longitudinal"] = long_tag[frame] if frame < len(long_tag) else "NA"
        row["lateral"] = lat_tag[frame] if frame < len(lat_tag) else "NA"

        writer.writerow(row)

print(f" Merged activity tags into: {OUT_PATH}")
