from load_data import load_image, list_images, load_json_array, load_csv
from filter import filter
from leading_edge import leading_edge
from projection import project, prepare_bearings
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def show(img, ranges, bearings):
    img = img[:len(ranges), :len(bearings)]

    angles = np.arctan2(bearings[:, 1], bearings[:, 0])
    angles_deg = np.degrees(angles)

    plt.figure(figsize=(6, 8))
    plt.imshow(
        img,
        cmap="gray",
        aspect="auto",
        extent=[
            angles_deg.min(),
            angles_deg.max(),
            ranges[-1],
            ranges[0],
        ],
    )
    plt.xlabel("bearing [deg]")
    plt.ylabel("range [m]")
    plt.title("Sonar image")
    plt.show()
    
def show_edge(img, edge):
    plt.figure(figsize=(6, 8))
    plt.imshow(img, cmap="gray")
    cols = edge >= 0
    plt.scatter(np.where(cols)[0], edge[cols], s=4)
    plt.show()

def show_points(points):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    o3d.visualization.draw_geometries([pcd])
    
# Load all the data files
files = list_images(DATA/"images")
ranges = load_json_array(DATA / "sonar_transform/range.json")
bearings = load_json_array(DATA / "sonar_transform/bearing.json")
imu = load_csv(DATA / "imu/imu.csv")

# Set parameters for image filter
threshold = 0.25
min_row = 100
tilt_deg = 30.0
image_stride = 3

debug_img = load_image(files[0])
filtered_img = filter(debug_img, 3)
edge = leading_edge(filtered_img, threshold, min_row)
prepared_bearings = prepare_bearings(bearings, tilt_deg=tilt_deg)
local_points = project(edge, ranges, prepared_bearings)

show(debug_img, ranges, bearings)
show(filtered_img, ranges, bearings)
show_edge(filtered_img, edge)
show_points(local_points)