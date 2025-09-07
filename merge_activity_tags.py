'''import csv
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
'''

import os
import csv
import json

# === CONFIG ===
TAG_DIR = "output_tags"

# === Loop through activity tag files ===
for fname in os.listdir(TAG_DIR):
    if fname.endswith("_activity_tags.json"):
        scenario_id = fname.replace("_activity_tags.json", "")
        tag_path = os.path.join(TAG_DIR, fname)
        csv_path = os.path.join(TAG_DIR, f"{scenario_id}_actor_dynamics.csv")
        out_path = os.path.join(TAG_DIR, f"{scenario_id}_actor_dynamics_tagged.csv")

        if not os.path.exists(csv_path):
            print(f"⚠️ Skipping {scenario_id}: no dynamics CSV found.")
            continue

        # Load tags
        with open(tag_path, "r") as f:
            tags = json.load(f)

        with open(csv_path, "r") as infile, open(out_path, "w", newline="") as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ["longitudinal", "lateral"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                actor_id = row["actor_id"]
                frame = int(row["frame"])
                long_tag = tags.get(actor_id, {}).get("longitudinal", [])
                lat_tag = tags.get(actor_id, {}).get("lateral", [])
                row["longitudinal"] = long_tag[frame] if frame < len(long_tag) else "NA"
                row["lateral"] = lat_tag[frame] if frame < len(lat_tag) else "NA"
                writer.writerow(row)

        print(f"✅ Merged tags into: {out_path}")
