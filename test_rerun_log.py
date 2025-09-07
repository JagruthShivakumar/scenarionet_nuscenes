import rerun as rr
import numpy as np
import time

rr.init("test_log")
rr.spawn()

time.sleep(1)  # Allow viewer to initialize

trajectory = np.array([[i, i * 0.5, 0] for i in range(10)])
rr.log("trajectory_path", rr.LineStrips3D([trajectory]))

time.sleep(3)  # Let viewer receive and render the data
