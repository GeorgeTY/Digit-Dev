import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from show_transform import dotDetection, dotMatching, dotRegistration
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
    print(TY.shape, G.shape, W.shape)
    np.savetxt("./output/saved_TY.out", TY, delimiter=",")
    np.savetxt("./output/saved_G.out", G, delimiter=",")
    np.savetxt("./output/saved_W.out", W, delimiter=",")
    np.savetxt("./output/saved_P.out", P * 100, delimiter=",", fmt="%d")
    for i in range(len(P[0])):
        print(np.max(P[0][i]) * 100)

    ## Numbering the dots
    # for i in range(len(X)):
    #     cv2.putText(
    #         Frm_dot_movement,
    #         "Ori:{}".format(i),
    #         (int(X[i][0]) * 2 + 5, int(X[i][1]) * 2 + 5),
    #         cv2.FONT_HERSHEY_SIMPLEX,
    #         0.5,
    #         (255, 0, 0),
    #         1,
    #     )
    for i in range(len(TY)):
        cv2.circle(
            Frm_dot_movement,
            (int(TY[i][0]) * 2, int(TY[i][1]) * 2),
            50,
            (0, 255, 255),
            1,
        )
        cv2.putText(
            Frm_dot_movement,
            "Y:{}".format(i),
            (int(Y[i][0]) * 2 + 35, int(Y[i][1]) * 2 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
        )

    # for i in range(P.shape[0]):
    #     for j in range(P.shape[1]):
    #         if dotPair[i][j] > 0:
    #             print("dotPair[{}][{}]: {}".format(i, j, dotPair[i][j]))
    ## Print the Probability of the dotPair
    for i in range(len(Y)):
        for j in range(len(Y)):
            print("({},{}), ".format(i, j), P[i][j])
            cv2.putText(
                Frm_dot_movement,
                "%.4f" % P[j][i],
                (int(X[i][0]) * 2 - 5, int(X[i][1]) * 2 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
            )
            pass

    cv2.imshow("Dot Movement", Frm_dot_movement)
    cv2.moveWindow("Dot Movement", 100, 100)

    toc = time.time()
    cv2.waitKey(0)
    print("Time: {}".format(toc - tic))

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
