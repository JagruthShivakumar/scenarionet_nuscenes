"""import os
from metadrive.envs.scenario_env import ScenarioEnv

# Path to your folder containing .pkl files
scenario_dir = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output/output_0"

# List all .pkl files in the folder
scenario_files = [f for f in os.listdir(scenario_dir) if f.endswith(".pkl")]
scenario_files.sort()  # Optional: ensures consistent order

# Loop through each .pkl file and run it
for file_name in scenario_files:
    file_path = os.path.join(scenario_dir, file_name)
    print(f"Running scenario: {file_name}")

    env = ScenarioEnv(dict(
        use_render=True,
        manual_control=True,
        decision_repeat=5,
        data_directory=scenario_dir,
        scenario_file_path=file_path  # <- Directly load this .pkl
    ))

    obs = env.reset()
    done = False
    while not done:
        obs, reward, terminated, truncated, info = env.step([0, 0])
        env.render()
        done = terminated or truncated

    env.close()
"""
"""import os
from metadrive.envs.scenario_env import ScenarioEnv

# === CONFIG ===
scenario_dir = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output"
steps_per_scenario = 1000
render = True
manual_control = False

# === Find all .pkl files ===
scenario_files = sorted([f for f in os.listdir(scenario_dir) if f.endswith(".pkl")])
print(f"Found {len(scenario_files)} scenarios.")

# === Run each scenario ===
for idx, scenario_file in enumerate(scenario_files):
    full_path = os.path.join(scenario_dir, scenario_file)
    print(f"\n▶ Running Scenario {idx + 1}: {scenario_file}")

    env = ScenarioEnv(dict(
        use_render=render,
        manual_control=manual_control,
        data_directory=scenario_dir,
        start_scenario_index=idx,
        num_scenarios=1,
        decision_repeat=5
    ))

    obs = env.reset()
    for _ in range(steps_per_scenario):
        obs, reward, terminated, truncated, info = env.step([0, 0])
        if render:
            env.render()
        if terminated or truncated:
            break
    env.close()
"""
import os
from metadrive.envs.scenario_env import ScenarioEnv

# === CONFIG ===
scenario_dir = "C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output/output_0"
steps_per_scenario = 1000
render = True
manual_control = False

# === Filter only valid scenario files ===
scenario_files = sorted([
    f for f in os.listdir(scenario_dir)
    if f.endswith(".pkl") and f.startswith("sd_nuscenes")
])

print(f" Found {len(scenario_files)} valid NuScenes scenarios.")

# === Run each scenario ===
for idx, scenario_file in enumerate(scenario_files):
    print(f"\n Running Scenario {idx + 1}/{len(scenario_files)}: {scenario_file}")

    env = ScenarioEnv(dict(
        use_render=render,
        manual_control=manual_control,
        data_directory=scenario_dir,
        start_scenario_index=idx,
        num_scenarios=1,
        decision_repeat=5
    ))

    obs = env.reset()

    for _ in range(steps_per_scenario):
        obs, reward, terminated, truncated, info = env.step([0, 0.3])  # add a little forward motion
        if render:
            env.render()
        if terminated or truncated:
            break

    env.close()
