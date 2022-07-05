import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from pycpd import AffineRegistration
from show_transform import dotDetection


tic = time.time()

Frm = cv2.imread("./pics/marker_movement/Frm.png")
Frm0 = cv2.imread("./pics/marker_movement/Frm0.png")
blobDetector = cv2.SimpleBlobDetector_create()
keypoints_Frm, frm_with_keypoints = dotDetection(blobDetector, Frm)
keypoints_Frm0, frm_with_keypoints0 = dotDetection(blobDetector, Frm0)
cv2.imshow("Keypoints", frm_with_keypoints)
cv2.imshow("Keypoints0", frm_with_keypoints0)

X = np.array([keypoint.pt for keypoint in keypoints_Frm])
Y = np.array([keypoint.pt for keypoint in keypoints_Frm0])

reg = AffineRegistration(**{"X": X, "Y": Y})
TY, ((s, R), t) = reg.register()

toc = time.time()
print("Time: {}".format(toc - tic))


cv2.waitKey(0)
cv2.destroyAllWindows()
