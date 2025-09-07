import numpy as np
from math import cos, sin, pi

def compute_vlong(vx, vy, yaw):
    return cos(yaw) * vx + sin(yaw) * vy

def tag_longitudinal_activity(track, alpha=0.01):
    tags = []
    vlong_series = []

    for state in track:
        vx = state["velocity"][0]
        vy = state["velocity"][1]
        yaw = state["heading"]
        length = state["length"]

        vlong = compute_vlong(vx, vy, yaw)
        vlong_series.append(vlong)

        if vlong < -alpha * length:
            tags.append("reversing")
        elif abs(vlong) <= alpha * length:
            tags.append("standing_still")
        else:
            tags.append("cruising")  # Placeholder, we refine later

    # Refine cruising → accelerating/decelerating using Δvlong
    for i in range(1, len(tags)):
        dv = vlong_series[i] - vlong_series[i-1]
        if tags[i] == "cruising":
            if dv > 0.2:
                tags[i] = "accelerating"
            elif dv < -0.2:
                tags[i] = "decelerating"

    return tags

def tag_lateral_activity(track, dt=0.1, turn_threshold_deg=45):
    yaw_series = [state["heading"] for state in track]
    tags = ["not_valid"] * len(track)

    # Convert threshold to radians
    turn_threshold = np.deg2rad(turn_threshold_deg)

    i = 0
    while i < len(yaw_series) - 1:
        yaw_rate = (yaw_series[i+1] - yaw_series[i]) / dt

        # Detect start of turn
        if abs(yaw_rate) > 0.1:
            start = i
            total_turn = 0.0
            direction = np.sign(yaw_rate)

            while i < len(yaw_series) - 1:
                dyaw = yaw_series[i+1] - yaw_series[i]
                total_turn += dyaw
                i += 1
                if abs(total_turn) > turn_threshold:
                    break

            label = "turning_left" if direction > 0 else "turning_right"
            for j in range(start, i + 1):
                tags[j] = label
        else:
            tags[i] = "going_straight"
            i += 1

    return tags
