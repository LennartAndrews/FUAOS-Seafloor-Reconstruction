from pathlib import Path
from load_data import list_images, load_json_array, load_csv
from mapping import build_map
import open3d as o3d

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPORTS = ROOT / "exports"

    
def show_points(points):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    o3d.visualization.draw_geometries([pcd])
     
def main():
    files = list_images(DATA/"images")
    fix = load_csv(DATA / "gps/fix.csv")
    ranges = load_json_array(DATA / "sonar_transform/range.json")
    bearings = load_json_array(DATA / "sonar_transform/bearing.json")
    imu = load_csv(DATA / "imu/imu.csv")
    
    threshold = 0.21
    tilt_deg = 30.0
    image_stride = 20

    points = build_map(files, fix, imu, ranges, bearings, threshold, tilt_deg, image_stride)
    
    show_points(points)


main()
    
