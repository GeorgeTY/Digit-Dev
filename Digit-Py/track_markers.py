from dis import dis
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from pycpd import AffineRegistration
from show_transform import dotDetection, dotMatching, dotRegistration


tic = time.time()
# Frm = cv2.imread("./pics/marker_movement/Frm.png")
Frm = cv2.imread("./pics/marker_movement/Frm_Lack.png")
Frm0 = cv2.imread("./pics/marker_movement/Frm0.png")
blobDetector = cv2.SimpleBlobDetector_create()
keypoints_Frm, Frm_with_keypoints = dotDetection(blobDetector, Frm)
keypoints_Frm0, Frm0_with_keypoints = dotDetection(blobDetector, Frm0)

X, Y, TY, s, R, t = dotRegistration(keypoints_Frm0, keypoints_Frm)
Frm_dot_movement, dotPair = dotMatching(X, Y, TY, Frm0, Frm)
# print("dotPair: \n", dotPair)
cv2.imshow("Dot Movement", Frm_dot_movement)
cv2.moveWindow("Dot Movement", 100, 100)

toc = time.time()
print("Time: {}".format(toc - tic))


cv2.waitKey(0)
cv2.destroyAllWindows()
