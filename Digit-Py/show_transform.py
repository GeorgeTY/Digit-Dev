import sys
import cv2
import csv
import numpy as np
import scipy.ndimage as ndi
import digit_interface as Digit


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
    frm_with_keypoints = cv2.drawKeypoints(
        Frm,
        keypoints,
        np.array([]),
        (50, 50, 150),
        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
    )
    for keypoint in keypoints:
        cv2.circle(
            frm_with_keypoints,
            (int(keypoint.pt[0]), int(keypoint.pt[1])),
            1,
            circleColor,
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
    return keypoints, frm_with_keypoints


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
        keypoints, frm_with_keypoints = dotDetection(blobDetector, Frm)

        cv2.imshow("Keypoints", frm_with_keypoints)
        cv2.moveWindow("Keypoints", 100, 100)

        getKey = cv2.waitKey(1)
        if getKey == 27:  # ESC
            break
        elif getKey == ord("o"):  # Get original frame
            Frm_a = Frm
            keypoints_a = keypoints
            print("Original Frame Got.")
        elif getKey == ord("c"):  # Capture difference
            digit.show_view(digit.get_frame())
            cv2.waitKey(0)
            break
        elif getKey == ord("d"):  # Show difference
            while True:
                Frm = digit.get_frame()
                keypoints_b, Frm_b = dotDetection(blobDetector, Frm)
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
                cv2.imshow("Difference", frm_with_keypoints)
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
