import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from show_transform import dotDetection, dotMatching, dotRegistration


tic = time.time()
# Frm = cv2.imread("./pics/marker_movement/Frm.png")
Frm = cv2.imread("./pics/marker_movement/Frm_Lack.png")
Frm0 = cv2.imread("./pics/marker_movement/Frm0.png")
blobDetector = cv2.SimpleBlobDetector_create()
keypoints_Frm, Frm_with_keypoints = dotDetection(blobDetector, Frm)
keypoints_Frm0, Frm0_with_keypoints = dotDetection(blobDetector, Frm0)

X, Y, TY, G, W = dotRegistration(keypoints_Frm0, keypoints_Frm)
dotRegistration(keypoints_Frm0, keypoints_Frm)
Frm_dot_movement, dotPair = dotMatching(X, Y, TY, Frm0, Frm)
# print("dotPair: \n", dotPair)

## Numbering the dots
for i in range(len(X)):
    cv2.putText(
        Frm_dot_movement,
        "Ori:{}".format(i),
        (int(X[i][0]) * 2 + 5, int(X[i][1]) * 2 + 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 0, 0),
        1,
    )
for i in range(len(TY)):
    cv2.circle(
        Frm_dot_movement, (int(TY[i][0]) * 2, int(TY[i][1]) * 2), 50, (0, 0, 255), 1
    )
    cv2.putText(
        Frm_dot_movement,
        "Mov:{}".format(i),
        (int(TY[i][0]) * 2 + 5, int(TY[i][1]) * 2 + 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1,
    )

print(G.shape)

## Print the Correspondence
for i in range(len(Y)):
    for j in range(len(Y)):
        # print("({},{}), ".format(i, j), G[i][j])
        # cv2.putText(
        #     Frm_dot_movement,
        #     "%.4f" % G[j][i],
        #     (int(X[i][0]) * 2 - 5, int(X[i][1]) * 2 - 5),
        #     cv2.FONT_HERSHEY_SIMPLEX,
        #     0.5,
        #     (0, 0, 255),
        #     1,
        # )
        pass

cv2.imshow("Dot Movement", Frm_dot_movement)
cv2.moveWindow("Dot Movement", 100, 100)

toc = time.time()
print("Time: {}".format(toc - tic))


cv2.waitKey(0)
cv2.destroyAllWindows()
