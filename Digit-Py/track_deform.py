import cv2
import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

points = np.loadtxt("./output/saved_X.out", delimiter=" ")
tri = Delaunay(points)

plt.triplot(points[:, 0], points[:, 1], tri.simplices)
plt.plot(points[:, 0], points[:, 1], "o")
plt.show()
