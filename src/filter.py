import cv2
import numpy as np

def normalize(x):
    x = x.astype(np.float32)
    x -= x.min()
    m = x.max()
    if m > 0:
        x /= m
    return x

def erode_3x1(img):
    kernel = np.ones((3, 1))
    return cv2.erode(img, kernel)


def dilate_3x1(img):
    kernel = np.ones((3, 1))
    return cv2.dilate(img, kernel)

def filter(img, ksize):
    x = normalize(img)
    x = np.clip(x, 0.0, 1.0)
    x = 255 * x
    
    x = cv2.medianBlur(x, ksize)
    x = erode_3x1(x)
    x = erode_3x1(x)
    x = dilate_3x1(x)
    x = dilate_3x1(x)
  
    return x / 255.0