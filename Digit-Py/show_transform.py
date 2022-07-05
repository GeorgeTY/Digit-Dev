import sys
import cv2
import time
import numpy as np
import digit_interface as Digit
import matplotlib.pyplot as plt
from pycpd import AffineRegistration


def connectDigit(intensity=8):
    digits = Digit.DigitHandler.list_digits()
    if len(digits) == 0:
        sys.exit("No Digit Found uwu")

    digit = Digit.Digit(digits[0]["serial"])
    digit.connect()
    digit.set_intensity(intensity)
    return digit


def setVideoEncoder():
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    videoOut = cv2.VideoWriter()
    videoOut.open("output.mp4", fourcc, 30, (640, 480))
    return videoOut


def setDetectionParams():
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

    return blobParams


def dotDetection(blobDetector, Frm, circleColor=(0, 0, 255)):
    keypoints = blobDetector.detect(Frm)
    Frm_with_keypoints = cv2.drawKeypoints(
        Frm,
        keypoints,
        np.array([]),
        (50, 50, 150),
        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
    )
    for keypoint in keypoints:
        cv2.circle(
            Frm_with_keypoints,
            (int(keypoint.pt[0]), int(keypoint.pt[1])),
            1,
            circleColor,
            -1,
        )
    Frm_with_keypoints = cv2.putText(
        Frm_with_keypoints,
        "{}".format(len(keypoints)),
        (5, 315),
        cv2.FONT_HERSHEY_COMPLEX,
        0.5,
        (255, 255, 255),
        1,
    )
    return keypoints, Frm_with_keypoints


def dotMatching(X, Y):
    for i in range(len(X)):
        for j in range(len(Y)):
            if np.linalg.norm(X[i] - Y[j]) < 10:
                return True
    return


def main():
    digit = connectDigit()

    for _ in range(30):  # Preheat the digit
        Frm0 = digit.get_frame()

    blobDetector = cv2.SimpleBlobDetector_create(setDetectionParams())
    videoOut = setVideoEncoder()
    print(
        "Press ESC to quit, O to capture Original, C to capture Difference, D to show Difference."
    )

    while True:
        Frm = digit.get_frame()

        ## Dot detection
        keypoints, Frm_with_keypoints = dotDetection(blobDetector, Frm)

        cv2.imshow("Keypoints", Frm_with_keypoints)
        cv2.moveWindow("Keypoints", 100, 100)

        getKey = cv2.waitKey(1)
        if getKey == 27:  # ESC
            break
        elif getKey == ord("o"):  # Get original frame
            Frm_a = Frm
            keypoints_a = keypoints
            X = np.array([keypoint.pt for keypoint in keypoints_a])
            print("Original Frame Got.")
        elif getKey == ord("c"):  # Capture difference
            digit.show_view(digit.get_frame())
            cv2.waitKey(0)
            break
        elif getKey == ord("d"):  # Show difference
            while True:
                Frm = digit.get_frame()
                keypoints_b, Frm_b = dotDetection(blobDetector, Frm)
                Y = np.array([keypoint.pt for keypoint in keypoints_b])
                TY, ((s, R), t) = AffineRegistration(
                    **{"X": X, "Y": Y}
                ).register()  ## CPD registration
                print("TY: ", TY)
                print("s: ", s)
                print("R: ", R)
                print("t: ", t)

                cv2.imshow("Difference", Frm_with_keypoints)
                getKey = cv2.waitKey(1)
                if getKey == 27:  # ESC
                    break
                cv2.moveWindow("Difference", 100, 500)
            break

    ## Turn off the digit
    videoOut.release()
    digit.disconnect()


if __name__ == "__main__":
    main()
