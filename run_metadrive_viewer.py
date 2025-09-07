from metadrive.envs.scenario_env import ScenarioEnv
import time

# Path to your output folder with dataset_summary.pkl
data_directory = "output"

config = {
    "use_render": True,
    "window_size": (1280, 720),
    "data_directory": data_directory,
    "start_scenario_index": 0,
    "num_scenarios": 1,
    "manual_control": True,
    "debug": False
}

env = ScenarioEnv(config)
obs = env.reset()

for step in range(1000):
    obs, reward, terminated, truncated, info = env.step([0, 0])
    done = terminated or truncated
    time.sleep(0.05)
    if done:
        obs = env.reset()

env.close()
