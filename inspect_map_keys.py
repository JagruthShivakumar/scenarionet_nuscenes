import pickle

# === CONFIG ===
PKL_PATH = "output/output_1/sd_nuscenes_v1.0-mini_scene-1100.pkl"  # change as needed

# === Load .pkl file ===
with open(PKL_PATH, "rb") as f:
    data = pickle.load(f)

print(f"📂 Top-level keys in {PKL_PATH}:")
print("--------------------------------------------------")
for key in data.keys():
    print(f"✅ {key}")

# === Common map-related keys to check ===
map_keys = [
    "crosswalks",
    "lane_segments",
    "stop_lines",
    "intersections",
    "sidewalks",
    "stop_signs",
    "yield_signs",
    "traffic_lights"
]

print("\n🔍 Map-related keys:")
print("--------------------------------------------------")
for key in map_keys:
    if key in data:
        value = data[key]
        count = len(value) if hasattr(value, '__len__') else "N/A"
        print(f"✅ {key:<20} — Present ({count} items)")
    else:
        print(f"❌ {key:<20} — Not found")
