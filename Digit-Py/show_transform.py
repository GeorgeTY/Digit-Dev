import sys
import cv2
import csv
import numpy as np
import scipy.ndimage as ndi
import digit_interface as Digit


def connectDigit():
    digits = Digit.DigitHandler.list_digits()
    if len(digits) == 0:
        sys.exit("No Digit Found uwu")

    digit = Digit.Digit(digits[0]["serial"])
    digit.connect()
    digit.set_intensity(8)
    return digit


def main():
    digit = connectDigit()

    # digit.show_view(digit.get_frame())  # Show difference

    # train_img = digit.get_frame()
    # train_img_bw = cv2.cvtColor(train_img, cv2.COLOR_BGR2GRAY)

    # orb = cv2.ORB_create()

    for _ in range(30):
        Frm0 = digit.get_frame()
    ## Show Frm0
    # cv2.imshow("Frm0", Frm0)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    ## GaussianBlur I0
    # kernel = np.ones((25, 25), np.float32) / (25 ** 2)
    # I0 = cv2.filter2D(Frm0, -1, kernel)
    # cv2.imshow("Background", I0)

    blobParams = cv2.SimpleBlobDetector_Params()

    blobParams.minThreshold = 0
    blobParams.maxThreshold = 255

    blobParams.filterByArea = True
    blobParams.minArea = 10
    blobParams.maxArea = 1000

    blobParams.filterByCircularity = True
    blobParams.minCircularity = 0.8

    blobParams.filterByConvexity = True
    blobParams.minConvexity = 0.8

    blobParams.filterByInertia = True
    blobParams.minInertiaRatio = 0.01

    blobDetector = cv2.SimpleBlobDetector_create(blobParams)

    while True:
        Frm = digit.get_frame()

        ## Gaussian Method
        # dI = Frm - I0
        # m = cv2.cvtColor(
        #     (cv2.threshold(dI, 180, 255, cv2.THRESH_BINARY)[1]), cv2.COLOR_BGR2GRAY
        # )
        # cv2.imshow("Difference", dI)
        # cv2.imshow("Mask", m)

        ## Dot detection
        keypoints = blobDetector.detect(Frm)
        frm_with_keypoints = cv2.drawKeypoints(
            Frm,
            keypoints,
            np.array([]),
            (50, 50, 150),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )

        ## Find circles grid
        # frm_with_keypoints_gray = cv2.cvtColor(frm_with_keypoints, cv2.COLOR_BGR2GRAY)
        # ret, corners = cv2.findCirclesGrid(
        #     frm_with_keypoints_gray, (3, 3), cv2.CALIB_CB_SYMMETRIC_GRID
        # )
        # if ret:
        #     cv2.drawChessboardCorners(frm_with_keypoints, (3, 3), corners, ret)

        for keypoint in keypoints:
            cv2.circle(
                frm_with_keypoints,
                (int(keypoint.pt[0]), int(keypoint.pt[1])),
                1,
                (0, 0, 255),
                -1,
            )
        frm_with_keypoints = cv2.putText(
            frm_with_keypoints,
            "{}".format(len(keypoints)),
            (5, 315),
            cv2.FONT_HERSHEY_COMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )
        cv2.imshow("Keypoints", frm_with_keypoints)

        # cv2.moveWindow("Background", 0, 100)
        # cv2.moveWindow("Difference", 400, 100)
        # cv2.moveWindow("Mask", 400, 530)
        # cv2.moveWindow("Keypoints", 800, 100)
        cv2.moveWindow("Keypoints", 100, 100)

        getKey = cv2.waitKey(1)
        if getKey == 27:  # ESC
            break
        elif getKey == ord("d"):  # Show difference
            digit.show_view(digit.get_frame())
            cv2.waitKey(0)
            break
        elif getKey == ord("o"):  # Get original frame
            keypoints_a = keypoints
            Frm_a = Frm
        elif getKey == ord("c"):  # Capture difference
            keypoints_b = keypoints
            Frm_b = Frm
            frm_with_keypoints = cv2.drawKeypoints(
                Frm,
                keypoints_a,
                np.array([]),
                (50, 50, 150),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            )
            for keypoint in keypoints_a:
                cv2.circle(
                    frm_with_keypoints,
                    (int(keypoint.pt[0]), int(keypoint.pt[1])),
                    1,
                    (0, 0, 255),
                    -1,
                )
            frm_with_keypoints = cv2.putText(
                frm_with_keypoints,
                "Frm_A: {}".format(len(keypoints_a)),
                (5, 315),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            frm_with_keypoints = cv2.drawKeypoints(
                frm_with_keypoints,
                keypoints_b,
                np.array([]),
                (150, 50, 50),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            )
            for keypoint in keypoints_b:
                cv2.circle(
                    frm_with_keypoints,
                    (int(keypoint.pt[0]), int(keypoint.pt[1])),
                    1,
                    (255, 0, 0),
                    -1,
                )
            frm_with_keypoints = cv2.putText(
                frm_with_keypoints,
                "Frm_B: {}".format(len(keypoints_b)),
                (100, 315),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            cv2.imshow("Captured", frm_with_keypoints)
            cv2.waitKey(0)
            break

    ## Turn off the digit
    digit.disconnect()


if __name__ == "__main__":
    main()
