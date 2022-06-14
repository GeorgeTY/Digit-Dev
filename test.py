import numpy as np

width, height = 640, 480
width_splitter, height_splitter = 640 / 4, 480 / 4
width_Distribution = np.arange(0, 640 + 1, width_splitter, dtype=int)
height_Distribution = np.arange(0, 480 + 1, height_splitter, dtype=int)
width_Distribution[-1] = width - 1
height_Distribution[-1] = height - 1
print(width_Distribution)
print(height_Distribution)
