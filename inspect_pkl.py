import pickle

pkl_path = r"C:\Users\kumar\OneDrive\Desktop\Research_Project\scenarionet_repo\output\output_0\sd_nuscenes_v1.0-mini_scene-0553.pkl"

with open(pkl_path, "rb") as f:
    data = pickle.load(f)

print("Top-level keys in the loaded .pkl file:")
print(list(data.keys()))
