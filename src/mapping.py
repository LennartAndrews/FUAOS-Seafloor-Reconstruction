# ChatGPT was used to assist in the implementation of GPS/IMU integration
# for building the global 3D map (mapping.py and imu.py)
# The overall program structure, concept, and final workflow were developed by the group.

from pathlib import Path
import numpy as np
from filter import filter
from leading_edge import leading_edge
from load_data import load_image
from projection import prepare_bearings, project
from imu import prepare_imu, estimate_roll_pitch, interp_roll_pitch, imu_rotation

EARTH_RADIUS_M = 6_371_000.0

# Transforming gps data into kartesian coordinates
def _prepare_fix(fix):
    fix = fix.copy()
    fix["timestamp"] = fix["timestamp"].astype(float)
    fix = fix.sort_values("timestamp").reset_index(drop=True) 

    lat = np.deg2rad(fix["latitude"].to_numpy(dtype=float))
    lon = np.deg2rad(fix["longitude"].to_numpy(dtype=float))
    lat0, lon0 = lat[0], lon[0]
    fix["x_east"] = (lon - lon0) * np.cos(lat0) * EARTH_RADIUS_M
    fix["y_north"] = (lat - lat0) * EARTH_RADIUS_M
    return fix

# If image is between two gps timestamps the images position has to be interpolated 
def _interpolate_xy(fix, timestamp):
    times = fix["timestamp"].to_numpy(dtype=float)
    return np.array(
        [
            np.interp(timestamp, times, fix["x_east"].to_numpy(dtype=float)),
            np.interp(timestamp, times, fix["y_north"].to_numpy(dtype=float)),
        ],
        dtype=float,
    )

# Calculate the direction in which the sonar is heading
def _heading_xy(fix, timestamp, dt=0.5):
    times = fix["timestamp"].to_numpy(dtype=float)
    t0 = max(timestamp - dt, float(times[0]))
    t1 = min(timestamp + dt, float(times[-1]))

    if t1 <= t0:
        return np.array([1.0, 0.0], dtype=float)

    direction = _interpolate_xy(fix, t1) - _interpolate_xy(fix, t0)
    norm = np.linalg.norm(direction)
    return direction / norm if norm else np.array([1.0, 0.0], dtype=float)

# Rotate local points to heading direction and shift them to the correct sonar position
def _to_global(local_points, position_xy, heading_xy):
    forward = heading_xy
    right = np.array([forward[1], -forward[0]], dtype=float)
    horizontal_global = np.outer(local_points[:, 0], forward) + np.outer(local_points[:, 1], right)

    global_points = np.empty_like(local_points)
    global_points[:, :2] = horizontal_global + position_xy
    global_points[:, 2] = local_points[:, 2]
    return global_points

# Create 3D map by creating a 3D projection for each image and append them into a global map with respect to sonar position
def build_map(image_files, fix, imu, ranges, bearings, threshold, tilt_deg, image_stride):
    stride = max(1, image_stride)
    indexed_files = list(enumerate(image_files))[::stride]

    fix = _prepare_fix(fix)
    imu = prepare_imu(imu)
    tilt = estimate_roll_pitch(imu)

    prepared_bearings = prepare_bearings(bearings, tilt_deg=tilt_deg)
    all_points = []

    for original_i, image_file in indexed_files:
        timestamp = float(Path(image_file).stem)

        img = filter(load_image(image_file), 3)
        min_row = 80 if original_i < 10000 else 200

        edge = leading_edge(img, threshold, min_row)
        local_points = project(edge, ranges, prepared_bearings)

        if local_points.size == 0:
            continue

        roll, pitch = interp_roll_pitch(tilt, timestamp)
        local_points = (imu_rotation(roll, pitch) @ local_points.T).T

        global_points = _to_global(
            local_points,
            _interpolate_xy(fix, timestamp),
            _heading_xy(fix, timestamp),
        )

        all_points.append(global_points)

    return np.vstack(all_points) if all_points else np.empty((0, 3), dtype=float)