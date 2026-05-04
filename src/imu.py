# ChatGPT was used to assist in the implementation of GPS/IMU integration
# for building the global 3D map (mapping.py and imu.py)
# The overall program structure, concept, and final workflow were developed by the group.

import numpy as np

def prepare_imu(imu):
    imu = imu.copy()
    imu["timestamp"] = imu["timestamp"].astype(float)
    imu = imu.sort_values("timestamp").reset_index(drop=True)
    return imu

def smooth(x, alpha=0.02):
    y = np.empty_like(x, dtype=float)
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = alpha * x[i] + (1 - alpha) * y[i - 1]
    return y

def estimate_roll_pitch(imu, alpha=0.02):
    ax = smooth(imu["linear_acceleration_x"].to_numpy(float), alpha)
    ay = smooth(imu["linear_acceleration_y"].to_numpy(float), alpha)
    az = smooth(imu["linear_acceleration_z"].to_numpy(float), alpha)

    roll = np.arctan2(ay, az)
    pitch = np.arctan2(-ax, np.sqrt(ay**2 + az**2))

    return {
        "t": imu["timestamp"].to_numpy(float),
        "roll": np.unwrap(roll),
        "pitch": np.unwrap(pitch),
    }

def interp_roll_pitch(tilt, timestamp):
    roll = np.interp(timestamp, tilt["t"], tilt["roll"])
    pitch = np.interp(timestamp, tilt["t"], tilt["pitch"])
    return roll, pitch

def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s,  c],
    ], dtype=float)

def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([
        [ c, 0, s],
        [ 0, 1, 0],
        [-s, 0, c],
    ], dtype=float)

def imu_rotation(roll, pitch):
    return rot_y(pitch) @ rot_x(roll)