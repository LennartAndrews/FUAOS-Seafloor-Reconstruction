import numpy as np

def prepare_bearings(bearings, tilt_deg):
    a = np.deg2rad(tilt_deg)
    c, s = np.cos(a), np.sin(a)
    R = np.array([[c, 0, s],
                  [0, 1, 0],
                  [-s, 0, c]])

    directions = np.asarray(bearings)[:, :3]
    norms = np.linalg.norm(directions, axis=1)
    prepared = np.zeros_like(directions)
    valid = norms > 0
    prepared[valid] = directions[valid] / norms[valid, None]
    return prepared @ R


def project(edge, ranges, prepared_bearings):
    cols = np.arange(min(len(edge), len(prepared_bearings)))
    rows = edge[: len(cols)]
    valid = (rows >= 0) & (rows < len(ranges))
    cols = cols[valid]
    rows = rows[valid].astype(int)
    distances = ranges[rows]
    return prepared_bearings[cols] * (-distances[:, None])
