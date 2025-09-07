from metadrive.envs.scenario_env import ScenarioEnv

env = ScenarioEnv(dict(
    use_render=True,
    manual_control=True,
    data_directory="C:/Users/kumar/OneDrive/Desktop/Research_Project/scenarionet_repo/output",  # <-- absolute path
    start_scenario_index=0,
    num_scenarios=1,
    decision_repeat=5
))

obs = env.reset()
for _ in range(1000):
    obs, reward, terminated, truncated, info = env.step([0, 0])
    env.render()
    if terminated or truncated:
        obs = env.reset()


env.close()
