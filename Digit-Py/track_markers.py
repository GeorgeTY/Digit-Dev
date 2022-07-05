from dis import dis
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from pycpd import AffineRegistration
from show_transform import dotDetection


def dotMatching(X, Y, TY, Frm):
    distance = np.zeros((len(X), len(Y)))
    dotPair = np.zeros((len(X), len(Y)))
    for i in range(len(X)):
        for j in range(len(TY)):
            distance[i][j] = np.linalg.norm(X[i] - TY[j])
        argmin_i = np.argmin(distance[i])
        print(np.min(distance[argmin_i]), ":", argmin_i)
        dotPair[i][argmin_i] = 1
        cv2.line(
            Frm,
            (int(X[i][0]), int(X[i][1])),
            (int(Y[np.argmin(distance[i])][0]), int(Y[np.argmin(distance[i])][1])),
            (0, 0, 255),
            2,
        )
    return Frm, dotPair


tic = time.time()
Frm = cv2.imread("./pics/marker_movement/Frm.png")
Frm0 = cv2.imread("./pics/marker_movement/Frm0.png")
blobDetector = cv2.SimpleBlobDetector_create()
keypoints_Frm, Frm_with_keypoints = dotDetection(blobDetector, Frm)
keypoints_Frm0, Frm0_with_keypoints = dotDetection(blobDetector, Frm0)

X = np.array([keypoint.pt for keypoint in keypoints_Frm])
Y = np.array([keypoint.pt for keypoint in keypoints_Frm0])

reg = AffineRegistration(**{"X": X, "Y": Y})
TY, ((s, R), t) = reg.register()
dotMovement, dotPair = dotMatching(X, Y, TY, Frm0)
print("dotPair: \n", dotPair)
dotMovement = cv2.addWeighted(Frm, 0.5, dotMovement, 0.5, 0)
cv2.imshow("Dot Movement", dotMovement)
cv2.moveWindow("Dot Movement", 100, 100)

toc = time.time()
print("Time: {}".format(toc - tic))


cv2.waitKey(0)
cv2.destroyAllWindows()
