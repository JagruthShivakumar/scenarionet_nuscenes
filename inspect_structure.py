import pickle

pkl_path = r"C:\Users\kumar\OneDrive\Desktop\Research_Project\scenarionet_repo\output\output_0\sd_nuscenes_v1.0-mini_scene-0553.pkl"

with open(pkl_path, "rb") as f:
    data = pickle.load(f)

print("Top-level keys:", list(data.keys()))
print()

# Try printing keys under dynamic_map_states and map_features
print("dynamic_map_states type:", type(data["dynamic_map_states"]))
print("map_features type:", type(data["map_features"]))

# Try to guess if there's trajectory info there
try:
    print("\nFirst map feature:")
    print(data["map_features"][0])
except Exception as e:
    print("Could not access map_features[0]:", e)

# If dynamic_map_states is a list, show one item
if isinstance(data["dynamic_map_states"], list):
    print("\nFirst dynamic map state:")
    print(data["dynamic_map_states"][0])

agent_id = "d5f34ea24e844aa284d3ebc1b057a918"
print(data.get(agent_id, "No direct agent data found"))
