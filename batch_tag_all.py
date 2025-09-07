# batch_tag_all.py
import os
import pickle
import json
import math
import csv

from taggers.activity_tags import tag_longitudinal_activity, tag_lateral_activity

# === CONFIG ===
INPUT_DIRS = [
    "output/output_0",
    "output/output_1"
]
OUTPUT_DIR = "output_tags"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_scenario_id(pkl_data):
    return pkl_data["metadata"].get("scenario_id", "unknown_scene")


def tag_scenario(pkl_path):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    scenario_id = extract_scenario_id(data)
    tracks = data["tracks"]
    activity_tags = {}

    for actor_id, actor in tracks.items():
        state = actor["state"]
        if not isinstance(state, dict):
            continue

        try:
            velocity = state["velocity"]
            heading = state["heading"]
            length = actor.get("metadata", {}).get("length", 4.0)

            track = []
            for i in range(len(velocity)):
                vx, vy = velocity[i]
                track.append({
                    "velocity": [vx, vy],
                    "heading": heading[i],
                    "length": length
                })

            activity_tags[actor_id] = {
                "longitudinal": tag_longitudinal_activity(track),
                "lateral": tag_lateral_activity(track)
            }
        except Exception as e:
            print(f"  ⚠️  Skipping actor {actor_id}: {e}")

    # Save activity tags
    tag_path = os.path.join(OUTPUT_DIR, f"{scenario_id}_activity_tags.json")
    with open(tag_path, "w") as f:
        json.dump(activity_tags, f, indent=2)

    print(f"  Activity tags saved to: {tag_path}")
    return scenario_id, data  # returning data to reuse


def save_dynamics_csv(scenario_id, data):
    dynamics_path = os.path.join(OUTPUT_DIR, f"{scenario_id}_actor_dynamics.csv")
    tracks = data["tracks"]

    with open(dynamics_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["actor_id", "type", "frame", "speed (m/s)", "heading (rad)", "yaw_rate (rad/s)"])

        for actor_id, actor in tracks.items():
            raw_type = actor.get("type", "").upper()
            if raw_type == "PEDESTRIAN": actor_type = "pedestrian"
            elif raw_type == "CYCLIST": actor_type = "bicycle"
            elif raw_type == "VEHICLE": actor_type = "car"
            elif raw_type == "TRAFFIC_BARRIER": actor_type = "barrier"
            elif raw_type == "EGO": actor_type = "ego"
            else: actor_type = "unknown"

            state = actor["state"]
            velocity = state["velocity"]
            heading = state["heading"]
            n = len(velocity)

            for i in range(n):
                vx, vy = velocity[i]
                speed = math.sqrt(vx ** 2 + vy ** 2)
                yaw = heading[i]
                yaw_rate = (heading[i] - heading[i - 1]) / 0.1 if i > 0 else 0.0
                writer.writerow([actor_id, actor_type, i, round(speed, 2), round(yaw, 3), round(yaw_rate, 3)])

    print(f"  Dynamics saved to: {dynamics_path}")
    return dynamics_path


# === MAIN ===
for folder in INPUT_DIRS:
    abs_dir = os.path.abspath(folder)
    for file in os.listdir(abs_dir):
        if file.endswith(".pkl") and file.startswith("sd_nuscenes"):
            pkl_path = os.path.join(abs_dir, file)
            scene_id, data = tag_scenario(pkl_path)
            _ = save_dynamics_csv(scene_id, data)

# You can now run merge_activity_tags.py separately to merge the JSON + dynamics CSV
print("\n Batch tagging and dynamics completed. Run merge_activity_tags.py separately to finish tagging.")
