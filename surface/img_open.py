import cv2 as cv
import numpy as np



image_c = cv.imread('t.png', cv.IMREAD_UNCHANGED)
image_c = cv.cvtColor(image_c, cv.COLOR_BGR2RGB)
print(image_c.shape)
print(image_c)
print()
img1_gray = cv.cvtColor(image_c , cv.COLOR_RGB2GRAY)
print(img1_gray.shape)
print(img1_gray)
print()

image_g = cv.imread('t.png', cv.IMREAD_GRAYSCALE)
print(image_g.shape)
print(image_g)

print(image_g == img1_gray)

print(cv.imread.__code__)