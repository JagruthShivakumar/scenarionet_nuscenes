# env_interaction_tags_enriched.py
# Runtime-enriched environment tagging for ScenarioNet .pkl files (NuScenes).
# - Loads ScenarioNet .pkl (tracks, metadata,...)
# - Attaches NuScenes map layers at runtime (crosswalks, stop_lines; easy to extend)
# - Emits per-frame, per-actor environment-interaction tags (Waymo-style)

import os, json, pickle, argparse, math
from glob import glob
import numpy as np
from tqdm import tqdm
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
from nuscenes.nuscenes import NuScenes
from nuscenes.map_expansion.map_api import NuScenesMap


# ---------- small geometry utils ----------
def to_polygon(coords):
    """coords: Nx2 array-like -> shapely Polygon (auto-fix if too few unique points)."""
    try:
        pts = [(float(x), float(y)) for x, y in coords]
    except Exception:
        return None
    if len(set(pts)) < 3:
        # Fall back to a buffered line if degenerate
        try:
            return LineString(pts).buffer(0.2)
        except Exception:
            return None
    try:
        poly = Polygon(pts)
        if not poly.is_valid:
            poly = poly.buffer(0)  # fix self-crossings
        return poly
    except Exception:
        return None


def list_polygons(nmap: NuScenesMap, layer: str):
    """
    Return a list of shapely Polygons for a given NuScenesMap layer.
    In this NuScenes devkit version, get_records_in_layer returns a list of tokens (strings).
    """
    polys = []
    try:
        tokens = nmap.get_records_in_layer(layer)  # list of string tokens
    except Exception:
        return polys

    for token in tokens:  # token is already a string
        try:
            poly_xy = nmap.extract_polygon(layer, token)
            poly = to_polygon(poly_xy)
            if poly is not None:
                polys.append(poly)
        except Exception:
            continue
    return polys


def min_distance(polys, pt):
    p = Point(pt[0], pt[1])
    if not polys:
        return float("inf")
    dmin = float("inf")
    for poly in polys:
        try:
            if hasattr(poly, "exterior") and poly.exterior:
                d = poly.exterior.distance(p)
            else:
                d = poly.distance(p)
            if d < dmin:
                dmin = d
        except Exception:
            continue
    return dmin


def any_contains(polys, pt):
    p = Point(pt[0], pt[1])
    for poly in polys:
        try:
            if poly.contains(p):
                return True
        except Exception:
            continue
    return False


def heading_from_vel(vx, vy):
    return math.atan2(vy, vx) if (abs(vx) + abs(vy)) > 1e-6 else None


def unit(vec):
    n = np.linalg.norm(vec)
    return vec / n if n > 1e-9 else vec


# ---------- coordinate transform helpers ----------
def get_map_name(meta: dict):
    # Try common fields to get NuScenes map name
    for k in ["map_name", "location", "log_location", "nuscenes_map_name"]:
        v = meta.get(k)
        if isinstance(v, str) and v:
            return v
    # reasonable default for mini set
    return "boston-seaport"


def local_to_global_builder(meta: dict):
    """
    Build f(xy_local)->xy_global based on metadata if available.
    If not available, pass-through (assume already in global frame).
    """
    M = meta.get("world_from_local") or meta.get("global_from_local") or None
    if isinstance(M, (list, tuple, np.ndarray)):
        M = np.array(M, dtype=float)
        if M.shape == (3, 3):
            def f(xy):
                v = np.array([xy[0], xy[1], 1.0], dtype=float)
                out = M @ v
                return np.array([out[0], out[1]])
            return f
        if M.shape == (4, 4):
            def f(xy):
                v = np.array([xy[0], xy[1], 0.0, 1.0], dtype=float)
                out = M @ v
                return np.array([out[0], out[1]])
            return f

    origin = meta.get("origin")
    if isinstance(origin, dict) and "xy" in origin:
        try:
            xy0 = np.array(origin["xy"], dtype=float)
            yaw = float(origin.get("yaw", 0.0))
            c, s = math.cos(yaw), math.sin(yaw)
            R = np.array([[c, -s], [s, c]], dtype=float)
            def f(xy):
                return xy0 + (R @ np.array(xy, dtype=float))
            return f
        except Exception:
            pass

    # default: identity (assume already global)
    return lambda xy: np.array(xy, dtype=float)


# ---------- tagging logic ----------
def tag_crosswalk_and_stopline(pt_g, speed, heading_vec, crosswalk_polys, stopline_polys):
    tags = []

    # Crosswalk: IN / APPROACHING
    in_cw = any_contains(crosswalk_polys, pt_g)
    if in_cw:
        tags.append("in_crosswalk")
    else:
        d_cw = min_distance(crosswalk_polys, pt_g)
        if crosswalk_polys and np.isfinite(d_cw):
            try:
                centroids = np.array([[p.centroid.x, p.centroid.y] for p in crosswalk_polys])
                deltas = centroids - np.array(pt_g)
                idx = int(np.argmin(np.linalg.norm(deltas, axis=1)))
                to_cw = unit(deltas[idx])
                if d_cw < 8.0 and heading_vec is not None and float(np.dot(heading_vec, to_cw)) > 0.5:
                    tags.append("approaching_crosswalk")
            except Exception:
                if d_cw < 6.0:
                    tags.append("approaching_crosswalk")

    # Stopline: STOPPED AT / APPROACHING
    if stopline_polys:
        try:
            stop_buf = unary_union([p.buffer(1.0) for p in stopline_polys])
        except Exception:
            stop_buf = None

        if stop_buf is not None:
            P = Point(pt_g[0], pt_g[1])
            try:
                in_stop_zone = stop_buf.contains(P)
            except Exception:
                in_stop_zone = False

            try:
                d_sl = stop_buf.exterior.distance(P)
            except Exception:
                try:
                    d_sl = stop_buf.distance(P)
                except Exception:
                    d_sl = float("inf")

            if in_stop_zone and speed < 0.2:
                tags.append("stopped_at_stopline")
            elif np.isfinite(d_sl) and d_sl < 6.0 and heading_vec is not None:
                try:
                    c = stop_buf.centroid
                    to_sl = unit(np.array([c.x - pt_g[0], c.y - pt_g[1]]))
                    if float(np.dot(heading_vec, to_sl)) > 0.3:
                        tags.append("approaching_stop")
                except Exception:
                    tags.append("approaching_stop")

    return tags


def process_scene(pkl_path, nusc: NuScenes, maps_cache, out_dir):
    with open(pkl_path, "rb") as f:
        sc = pickle.load(f)

    meta = sc.get("metadata", {})
    map_name = get_map_name(meta)
    if map_name not in maps_cache:
        maps_cache[map_name] = NuScenesMap(dataroot=nusc.dataroot, map_name=map_name)
    nmap = maps_cache[map_name]

    # Preload polygons
    crosswalks = list_polygons(nmap, "ped_crossing")
    stoplines  = list_polygons(nmap, "stop_line")

    local2global = local_to_global_builder(meta)

    result = {
        "scene_file": os.path.basename(pkl_path),
        "map_name": map_name,
        "actors": {}
    }

    tracks = sc.get("tracks", [])
    for tr in tracks:
        tid = tr.get("id", tr.get("track_id"))
        if tid is None:
            continue

        states = tr.get("states") or tr.get("trajectory") or []
        actor_tags = []
        for i, st in enumerate(states):
            x = st.get("x"); y = st.get("y")
            if x is None and "position" in st:
                try:
                    x, y = float(st["position"][0]), float(st["position"][1])
                except Exception:
                    actor_tags.append({"frame": i, "tags": []})
                    continue
            if x is None or y is None:
                actor_tags.append({"frame": i, "tags": []})
                continue

            vx = st.get("vx", st.get("vel_x", 0.0))
            vy = st.get("vy", st.get("vel_y", 0.0))
            try:
                speed = float(math.hypot(float(vx), float(vy)))
            except Exception:
                speed = 0.0
            hdg = heading_from_vel(float(vx), float(vy))
            heading_vec = np.array([math.cos(hdg), math.sin(hdg)]) if hdg is not None else None

            try:
                pt_g = local2global([x, y])
            except Exception:
                pt_g = np.array([x, y], dtype=float)

            tags = tag_crosswalk_and_stopline(pt_g, speed, heading_vec, crosswalks, stoplines)
            actor_tags.append({"frame": i, "tags": tags})

        result["actors"][str(tid)] = actor_tags

    base = os.path.splitext(os.path.basename(pkl_path))[0]
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, base + "_envtags.json")
    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)
    return out_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Folder with ScenarioNet .pkl scenes (e.g., output/output_0)")
    ap.add_argument("--out", required=True, help="Output folder for *_envtags.json")
    ap.add_argument("--nusc_dataroot", required=True, help="NuScenes dataroot (e.g., .../Mini_testdata)")
    ap.add_argument("--version", default="v1.0-mini", help="NuScenes version (e.g., v1.0-mini or v1.0-trainval)")
    args = ap.parse_args()

    nusc = NuScenes(version=args.version, dataroot=args.nusc_dataroot, verbose=False)
    maps_cache = {}

    pkl_files = sorted([p for p in glob(os.path.join(args.input, "*.pkl")) if os.path.basename(p).startswith("sd_nuscenes")])
    if not pkl_files:
        print(f"[WARN] No sd_nuscenes*.pkl found under {args.input}")
        return

    print(f"Found {len(pkl_files)} file(s). Starting tagging with runtime map enrichment...")
    for p in tqdm(pkl_files):
        try:
            _ = process_scene(p, nusc, maps_cache, args.out)
        except Exception as e:
            print(f"[ERR] {os.path.basename(p)} -> {e}")
    print("Done.")


if __name__ == "__main__":
    main()
