import pickle

pkl_path = r"C:\Users\kumar\OneDrive\Desktop\Research_Project\scenarionet_repo\output\output_0\sd_nuscenes_v1.0-mini_scene-0553.pkl"

with open(pkl_path, "rb") as f:
    data = pickle.load(f)

print("Top-level keys:", data.keys())

print("\nFirst few entries in 'tracks':")
tracks = data["tracks"]
for i, t in enumerate(tracks):
    print(f"{i}: {t}")
    if i >= 4:
        break

# Try checking what data["metadata"] or others contain
print("\nmetadata keys:", list(data["metadata"].keys()))

# Try inspecting anything that might contain full data
for key in data.keys():
    if isinstance(data[key], (list, dict)) and key not in ['metadata', 'map_features', 'dynamic_map_states', 'tracks']:
        print(f"\n==== Inspecting key: {key} ====")
        print(type(data[key]))
        try:
            if isinstance(data[key], list):
                print(data[key][0])
            elif isinstance(data[key], dict):
                print(list(data[key].keys())[:5])
        except Exception as e:
            print("Could not inspect:", e)
