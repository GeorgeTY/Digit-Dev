from io import RawIOBase
import cv2
import img_to_depth_digit as itd
import time
# from classdef import Lookuptable          #报错
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from panda3d.core import NodePath
import visualization.panda.world as world
from modeling.geometric_model import gen_pointcloud
import modeling.geometric_model as gm
import visualization.panda.world as wd

# image = cv2.imread("/home/jhz/桌面/gelsight_resconstruct/digit-main/fabric_edges_images/tst0.jpg")
image = cv2.imread("/home/jhz/桌面/gelsight_resconstruct/digit-main/OpticalFlow/tst4.jpg")


frame = image
itd_cvter = itd.ImageToDepth("./digiteye/calibrate_new")

depth, hm ,grad= itd_cvter.convert(frame)
f=open("Point_Cloud.txt",mode='w')

for i in range(0,hm.shape[0]-1,1):
    for j in range(0,hm.shape[1]-1,1):
        f.write(str(i)+' ')
        f.write(str(j)+' ')
        f.write(str(5*hm[i][j]))
        f.write('\n')

f.close()

#########################mathplot show##########################
# s1, s2 = np.shape(hm)[:2]
# #   plot the depth pic
# fig = plt.figure()
# # fig.set_size_inches(30,10)
# ax = Axes3D(fig)
# X = np.arange(0, s2)
# Y = np.arange(0, s1)
# X, Y = np.meshgrid(X, Y)
# ax.set_zlim3d(0, 10)
# ax.get_proj = lambda: np.dot(Axes3D.get_proj(ax), np.diag([1, 1, 0.3, 1]))
# ax.plot_surface(X, Y, hm, rstride=1, cstride=1, cmap='rainbow')

# plt.show()
################################################################

########################panda3d show############################
base = world.World(cam_pos=[.03, .03, .07], lookat_pos=[0.015, 0.015, 0])
pointcloud = None

pcdm = []
pcdm.append(None)
pcdm[0] = gm.GeometricModel(depth*.001)
pcdm[0].attach_to(base)

base.run()
###############################################################