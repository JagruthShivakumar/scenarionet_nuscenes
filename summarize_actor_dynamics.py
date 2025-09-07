import os
import pickle
import csv
import math

# === CONFIG ===
SCENARIO_PATH = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output/output_0/sd_nuscenes_v1.0-mini_scene-0553.pkl"
SAVE_DYNAMICS_PATH = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output_tags/scene-0553_actor_dynamics.csv"
SAVE_TYPEMAP_PATH = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output_tags/scene-0553_actor_type_map.csv"

# === Load scenario ===
with open(SCENARIO_PATH, "rb") as f:
    data = pickle.load(f)

tracks = data["tracks"]
print(f"Loaded scenario with {len(tracks)} actors.")

# === Write actor dynamics CSV ===
with open(SAVE_DYNAMICS_PATH, "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["actor_id", "type", "frame", "speed (m/s)", "heading (rad)", "yaw_rate (rad/s)"])

    for actor_id, actor in tracks.items():
        raw_type = actor.get("type", "").upper()

        if raw_type == "PEDESTRIAN":
            actor_type = "pedestrian"
        elif raw_type == "CYCLIST":
            actor_type = "bicycle"
        elif raw_type == "VEHICLE":
            actor_type = "car"
        elif raw_type == "TRAFFIC_BARRIER":
            actor_type = "barrier"
        elif raw_type == "EGO":
            actor_type = "ego"
        else:
            actor_type = "unknown"

        state = actor["state"]
        velocity = state["velocity"]
        heading = state["heading"]
        n = len(velocity)

        for i in range(n):
            vx, vy = velocity[i]
            speed = math.sqrt(vx ** 2 + vy ** 2)
            yaw = heading[i]
            yaw_rate = (heading[i] - heading[i - 1]) / 0.1 if i > 0 else 0.0  # 10Hz sampling

            writer.writerow([actor_id, actor_type, i, round(speed, 2), round(yaw, 3), round(yaw_rate, 3)])

print(f"\n✅ Saved per-frame actor dynamics to: {SAVE_DYNAMICS_PATH}")

# === Write actor_id → type map CSV ===
with open(SAVE_TYPEMAP_PATH, "w", newline='') as mapfile:
    map_writer = csv.writer(mapfile)
    map_writer.writerow(["actor_id", "type"])
    for actor_id, actor in tracks.items():
        raw_type = actor.get("type", "").upper()

        if raw_type == "PEDESTRIAN":
            actor_type = "pedestrian"
        elif raw_type == "CYCLIST":
            actor_type = "bicycle"
        elif raw_type == "VEHICLE":
            actor_type = "car"
        elif raw_type == "TRAFFIC_BARRIER":
            actor_type = "barrier"
        elif raw_type == "EGO":
            actor_type = "ego"
        else:
            actor_type = "unknown"

        map_writer.writerow([actor_id, actor_type])

print(f" Saved actor type map to: {SAVE_TYPEMAP_PATH}")
