import sys
import cv2
import time
import numpy as np
import digit_interface as Digit
import matplotlib.pyplot as plt
from pycpd import AffineRegistration

# ifVGA = True
ifVGA = False


def connectDigit(intensity=8):
    digits = Digit.DigitHandler.list_digits()
    if len(digits) == 0:
        sys.exit("No Digit Found uwu")

    digit = Digit.Digit(digits[0]["serial"])
    digit.connect()
    digit.set_intensity(intensity)
    if ifVGA:
        digit.set_resolution(digit.STREAMS["VGA"])
    return digit


def setVideoEncoder(scale=2):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    videoOut = cv2.VideoWriter()
    if ifVGA:
        videoOut.open("output.mp4", fourcc, 30, (480 * scale, 640 * scale))
    else:
        videoOut.open("output.mp4", fourcc, 30, (240 * scale, 320 * scale))
    return videoOut


def setDetectionParams():
    blobParams = cv2.SimpleBlobDetector_Params()

    blobParams.minThreshold = 0
    blobParams.maxThreshold = 255

    if ifVGA:
        blobParams.filterByArea = True
        blobParams.minArea = 50
        blobParams.maxArea = 500
    else:
        blobParams.filterByArea = True
        blobParams.minArea = 20
        blobParams.maxArea = 100

    blobParams.filterByCircularity = True
    blobParams.minCircularity = 0.7

    # blobParams.filterByConvexity = True
    # blobParams.minConvexity = 0.8

    # blobParams.filterByInertia = True
    # blobParams.minInertiaRatio = 0.01

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


def dotRegistration(keypoints_a, keypoints_b):
    X = np.array([keypoint.pt for keypoint in keypoints_a])
    Y = np.array([keypoint.pt for keypoint in keypoints_b])
    TY, ((s, R), t) = AffineRegistration(
        **{"X": X, "Y": Y}
    ).register()  ## CPD registration

    return X, Y, TY, s, R, t


def dotMatching(X, Y, TY, Frm0, Frm, scale=2):
    distance, dotPair = np.zeros((len(X), len(Y))), np.zeros((len(X), len(Y)))

    Frm_dot_movement = cv2.addWeighted(Frm, 0.65, Frm0, 0.35, 0)
    Frm_dot_movement = cv2.resize(
        Frm_dot_movement,
        (scale * Frm_dot_movement.shape[1], scale * Frm_dot_movement.shape[0]),
        interpolation=cv2.INTER_AREA,
    )

    for i in range(len(X)):
        for j in range(len(TY)):
            distance[i][j] = np.linalg.norm(X[i] - TY[j])
        argmin_i = np.argmin(distance[i])

        ## Temporary Implementation: Prevent the dot from being registered twice
        while dotPair[i][argmin_i] == 1:
            distance[i][argmin_i] = np.inf
            argmin_i = np.argmin(distance[i])

        dotPair[i][argmin_i] = 1
        cv2.arrowedLine(
            Frm_dot_movement,
            (int(X[i][0]) * scale, int(X[i][1]) * scale),
            (
                int(Y[argmin_i][0] * scale),
                int(Y[argmin_i][1]) * scale,
            ),
            (0, 0, 255),
            2,
        )
    return Frm_dot_movement, dotPair


def main():
    digit = connectDigit()
    for _ in range(30):  # Preheat the digit
        Frm0 = digit.get_frame()

    videoOut = setVideoEncoder()
    print(
        "Press ESC to quit, O to capture Original, C to capture Difference, D to show Difference."
    )

    blobDetector = cv2.SimpleBlobDetector_create(setDetectionParams())

    while True:
        Frm = digit.get_frame()

        ## Dot detection
        keypoints, Frm_with_keypoints = dotDetection(blobDetector, Frm)

        cv2.imshow("Preview", Frm_with_keypoints)
        cv2.moveWindow("Preview", 100, 100)

        getKey = cv2.waitKey(1)
        if getKey == 27 or getKey == ord("q"):  # ESC or q
            break
        if len(keypoints) == 0:  # No dot detected cause error
            continue
        elif getKey == ord("o"):  # Get original frame
            Frm_a = Frm
            keypoints_a = keypoints
            Frm_a_with_keypoints = Frm_with_keypoints
            print("Original Frame Got.")
            cv2.imshow("Original", Frm_a_with_keypoints)
            cv2.moveWindow("Original", 100, 550)
        elif getKey == ord("c"):  # Capture difference
            digit.show_view(digit.get_frame())
            cv2.waitKey(0)
            break
        elif getKey == ord("d"):  # Show difference
            while True:
                Frm = digit.get_frame()
                Frm_b = Frm
                keypoints_b, Frm_b_with_keypoints = dotDetection(blobDetector, Frm)

                ## Temporary implementation
                if len(keypoints_a) != len(keypoints_b):
                    continue

                X, Y, TY, s, R, t = dotRegistration(keypoints_a, keypoints_b)
                Frm_dot_movement, dotPair = dotMatching(X, Y, TY, Frm_a, Frm_b)

                videoOut.write(Frm_dot_movement)

                cv2.destroyWindow("Preview")
                cv2.moveWindow("Original", 100, 100)
                cv2.imshow("Dot Movement", Frm_dot_movement)
                cv2.moveWindow("Dot Movement", 490, 100)
                cv2.imshow("Current", Frm_b_with_keypoints)
                cv2.moveWindow("Current", 100, 550)
                getKey = cv2.waitKey(1)
                if getKey == 27 or getKey == ord("q"):  # ESC or q
                    break
            break

    ## Turn off the digit
    videoOut.release()
    print("Video saved to ./output.mp4")
    digit.disconnect()


if __name__ == "__main__":
    main()
