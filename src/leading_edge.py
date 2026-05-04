def leading_edge(img, threshold, min_row):
    m = img[min_row:] > threshold
    r = m.argmax(0) + min_row
    r[~m.any(0)] = -1
    return r