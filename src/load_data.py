from pathlib import Path
import json
import numpy as np
import pandas as pd
from PIL import Image

def list_images(folder):
    return sorted(Path(folder).glob("*.png"))

def load_image(path):
    return np.asarray(Image.open(path).convert("L"))

def load_json_array(path):
    with open(path, encoding="utf-8") as f:
        return np.asarray(json.load(f), dtype=float)
    
def load_csv(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    return df