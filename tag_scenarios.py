import os
import pickle
import json
from taggers.activity_tags import tag_longitudinal_activity, tag_lateral_activity

# === CONFIG ===
SCENARIO_PATH = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output/output_0/sd_nuscenes_v1.0-mini_scene-0553.pkl"
SAVE_DIR = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output_tags"
os.makedirs(SAVE_DIR, exist_ok=True)

# === Load scenario ===
with open(SCENARIO_PATH, "rb") as f:
    data = pickle.load(f)

tracks = data["tracks"]
print(f"Loaded scenario with {len(tracks)} actors.")

scenario_tags = {}

# === Loop through actors ===
for actor_id, actor_states in tracks.items():
    print(f"Processing actor: {actor_id} | Keys: {list(actor_states.keys())}")

    if "state" not in actor_states or not isinstance(actor_states["state"], dict):
        print(f"Skipping actor {actor_id} — 'state' missing or invalid.")
        continue

    state_data = actor_states["state"]
    num_frames = len(state_data["velocity"])  # all time series should be same length

    track = []
    for i in range(num_frames):
        entry = {
            "velocity": state_data["velocity"][i],     # [vx, vy]
            "heading": state_data["heading"][i],       # in radians
            "length": actor_states["metadata"].get("length", 4.0)
        }
        track.append(entry)

    # === Tagging
    long_tags = tag_longitudinal_activity(track)
    lat_tags = tag_lateral_activity(track)

    scenario_tags[actor_id] = {
        "longitudinal": long_tags,
        "lateral": lat_tags
    }

# === Save tags to file ===
scene_id = data["metadata"]["scenario_id"]
output_path = os.path.join(SAVE_DIR, f"{scene_id}_activity_tags.json")

with open(output_path, "w") as f:
    json.dump(scenario_tags, f, indent=2)

print(f"\n✅ Saved tags to {output_path}")
