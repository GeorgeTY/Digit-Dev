import sys
from tkinter import Frame
import cv2
import csv
import numpy as np
import digit_interface as Digit


def connectDigit():
    digits = Digit.DigitHandler.list_digits()
    if len(digits) == 0:
        sys.exit("No Digit Found")

    digit = Digit.Digit(digits[0]["serial"])
    digit.connect()
    digit.set_intensity(8)
    return digit


def main():
    digit = connectDigit()

    # digit.show_view()

    detector = cv2.SimpleBlobDetector_create()
    while True:
        # frame = cv2.cvtColor(digit.get_frame(), cv2.COLOR_BGR2GRAY)
        frame = digit.get_frame()

        keypoints = detector.detect(frame)
        im_with_keypoints = cv2.drawKeypoints(
            frame,
            keypoints,
            np.array([]),
            (0, 0, 255),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )
        cv2.imshow("Keypoints", im_with_keypoints)
        if cv2.waitKey(1) == 27:
            break
    digit.disconnect()


if __name__ == "__main__":
    main()
