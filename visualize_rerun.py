import rerun as rr
import numpy as np
import pickle
import time
import os

# === CONFIG ===
SCENARIO_PATH = r"C:\Users\kumar\OneDrive\Desktop\Research_Project\scenarionet_repo\output\output_0\sd_nuscenes_v1.0-mini_scene-0553.pkl"

def load_scenario(pkl_path):
    if not os.path.exists(pkl_path):
        raise FileNotFoundError(f"Scenario file not found: {pkl_path}")
    with open(pkl_path, "rb") as f:
        return pickle.load(f)

def log_agent_trajectories(scenario):
    rr.init("scenarionet_tracks")
    rr.spawn()
    time.sleep(1)  # Wait for viewer to initialize

    for track in scenario["tracks"]:
        # Skip if track is not a dictionary
        if not isinstance(track, dict):
            print(f"Skipping invalid track: {track}")
            continue

        obj_id = track.get("id", "unknown")

        # Ensure trajectory and position exist
        traj_info = track.get("trajectory", {})
        positions = traj_info.get("position", [])
        if not positions or len(positions) < 2:
            continue

        traj = np.array(positions)
        if traj.shape[1] != 3:
            print(f"Skipping badly shaped trajectory for {obj_id}: {traj.shape}")
            continue

        # Log as connected line
        stream_name = f"agent/{obj_id}"
        rr.log(stream_name, rr.LineStrips3D([traj]))

    time.sleep(3)  # Allow time to render before exiting

def main():
    print("Loading scenario...")
    scenario = load_scenario(SCENARIO_PATH)

    print("Visualizing in Rerun...")
    log_agent_trajectories(scenario)
    print("Done.")

if __name__ == "__main__":
    main()
