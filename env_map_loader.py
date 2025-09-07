from nuscenes.nuscenes import NuScenes
from nuscenes.map_expansion.map_api import NuScenesMap
from shapely.geometry import Polygon, LineString
import numpy as np


def get_scene_patch(nusc, scene_token, margin=50):
    """
    Compute bounding box (x_min, y_min, x_max, y_max) around ego poses of a scene.
    margin = extra space in meters.
    """
    scene = nusc.get("scene", scene_token)
    sample_token = scene["first_sample_token"]

    xs, ys = [], []
    while sample_token:
        sample = nusc.get("sample", sample_token)
        lidar_sd = nusc.get("sample_data", sample["data"]["LIDAR_TOP"])
        ego_pose = nusc.get("ego_pose", lidar_sd["ego_pose_token"])
        xs.append(ego_pose["translation"][0])
        ys.append(ego_pose["translation"][1])
        sample_token = sample["next"]

    return (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)


def extract_env_polygons(nusc_map, patch_box=None):
    """
    Extract polygons and centerlines for tagging.
    patch_box = (x_min, y_min, x_max, y_max). If None, use a very large area.
    """
    out = {"LANE": [], "LANE_CONNECTOR": [], "PED_CROSSING": [], "WALKWAY": [], "STOP_LINE": []}

    if patch_box is None:
        patch = (-1e4, -1e4, 1e4, 1e4)  # big box to cover map
    else:
        patch = patch_box

    layers = ["lane", "lane_connector", "ped_crossing", "walkway", "stop_line"]

    # Query map (old API uses positional args)
    records = nusc_map.get_records_in_patch(patch, layers, "intersect")

    # Polygons
    for layer in ["ped_crossing", "walkway", "stop_line"]:
        for token in records.get(layer, []):
            rec = nusc_map.get(layer, token)
            if "polygon" in rec and rec["polygon"]:
                out[layer.upper()].append(Polygon(np.array(rec["polygon"])))

    # Lanes & connectors
    for layer in ["lane", "lane_connector"]:
        for token in records.get(layer, []):
            rec = nusc_map.get(layer, token)
            pts = []
            for node_token in rec.get("baseline_path", []):
                node = nusc_map.get("node", node_token)
                pts.append((node["x"], node["y"]))
            if len(pts) >= 2:
                out[layer.upper()].append(LineString(pts))

    return out


if __name__ == "__main__":
    dataroot = "C:/Users/kumar/OneDrive/Desktop/Research_Project/Mini_testdata"
    nusc = NuScenes(version="v1.0-mini", dataroot=dataroot, verbose=False)

    # Get first scene and its map
    scene_token = nusc.scene[0]['token']
    scene = nusc.get('scene', scene_token)
    log = nusc.get('log', scene['log_token'])
    map_name = log['location']

    nusc_map = NuScenesMap(dataroot=dataroot, map_name=map_name)

    # Option A: large ego patch
    patch_box = get_scene_patch(nusc, scene_token, margin=2000)

    # Option B: global box (force full map scan)
    # patch_box = (-5000, -5000, 5000, 5000)

    env = extract_env_polygons(nusc_map, patch_box=patch_box)

    print("Extracted features inside expanded bounding box:")
    for k, v in env.items():
        print(f"{k}: {len(v)} objects")


    print("Extracted features inside ego bounding box:")
    for k, v in env.items():
        print(f"{k}: {len(v)} objects")
print("All geometric layers:", nusc_map.geometric_layers)

for layer in ["drivable_area", "road_segment", "road_block", "ped_crossing", "walkway", "stop_line"]:
    try:
        recs = nusc_map.get_records_in_patch((-500, -500, 500, 500), [layer], "intersect")
        print(f"{layer}: {sum(len(v) for v in recs.values())} records in patch")
    except Exception as e:
        print(f"{layer}: error {e}")
