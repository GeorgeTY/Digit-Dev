import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from show_transform import dotDetection, dotMatching, dotRegistration
from scipy.spatial import Delaunay
from global_params import *


def main():

    tic = time.time()
    Frm = cv2.imread("./pics/marker_movement/Frm.png")
    # Frm = cv2.imread("./pics/marker_movement/Frm_Lack.png")
    Frm0 = cv2.imread("./pics/marker_movement/Frm0.png")
    blobDetector = cv2.SimpleBlobDetector_create()
    keypoints_Frm, Frm_with_keypoints = dotDetection(blobDetector, Frm)
    keypoints_Frm0, Frm0_with_keypoints = dotDetection(blobDetector, Frm0)

    X, Y, TY, G, W, P = dotRegistration(keypoints_Frm0, keypoints_Frm)
    Frm_dot_movement, dotPair = dotMatching(X, Y, TY, P, Frm0, Frm)
    # np.savetxt("./output/saved_TY.out", TY, delimiter=",")
    # np.savetxt("./output/saved_G.out", G, delimiter=",")
    # np.savetxt("./output/saved_W.out", W, delimiter=",")
    np.savetxt("./output/saved_X.out", X, delimiter=" ")
    # np.savetxt("./output/saved_P.out", P * 100, delimiter=",", fmt="%d")

    tri = Delaunay(X)
    for simplex in tri.simplices:
        simplex = np.append(simplex, simplex[0])
        print(simplex)
        for i in range(len(simplex) - 1):
            cv2.line(
                Frm_dot_movement,
                (int(X[simplex[i]][0] * 2), int(X[simplex[i]][1] * 2)),
                (int(X[simplex[i + 1]][0] * 2), int(X[simplex[i + 1]][1] * 2)),
                (0, 255, 255),
                2,
            )

    # Calculate the distance
    # distance = np.zeros((len(P[0]), len(P[1])))
    # for i in range(len(X)):
    #     for j in range(len(TY)):
    #         if dotPair[i][j] > 0:
    #             distance[i][j] = np.linalg.norm(X[i] - TY[j])
    #         else:
    #             distance[i][j] = np.inf

    # print("Distance:")
    # for i in range(len(X)):
    #     for j in range(len(Y)):
    #         if dotPair[i][j] > 0:
    #             print("({},{}), ".format(i, j), distance[i][j])
    #             cv2.putText(
    #                 Frm_dot_movement,
    #                 "%.4f" % P[j][i],
    #                 (int(X[i][0]) * 2 - 5, int(X[i][1]) * 2 - 5),
    #                 cv2.FONT_HERSHEY_SIMPLEX,
    #                 0.5,
    #                 (0, 0, 255),
    #                 1,
    #                 cv2.LINE_AA,
    #             )
    #             pass

    cv2.imshow("Dot Movement", Frm_dot_movement)
    cv2.moveWindow("Dot Movement", 100, 100)

    toc = time.time()
    cv2.waitKey(0)
    print("Time: {}".format(toc - tic))

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
