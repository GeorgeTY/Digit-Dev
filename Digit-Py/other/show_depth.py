import cv2
import img_to_depth_digit as itd
import time
import matplotlib.pyplot as plt
from gelsight import gsdevice


itd_cvter = itd.ImageToDepth(
    "/home/jiangxin/uwu-dev/Digit-Dev/Digit-Py/digiteye/calibrate_gsmini_0329_1"
)


# video1 = cv2.VideoCapture(0)
# width = int(video1.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(video1.get(cv2.CAP_PROP_FRAME_HEIGHT))
# width = 320
# height = 240
def gsmini_connect():
    dev = gsdevice.Camera(gsdevice.Finger.MINI, dev_id=0)
    dev.connect()
    return dev


gsmini = gsmini_connect()

plt.ion()

try:
    while True:
        tic = time.time()

        plt.cla()
        # frame = video1.read()
        frame = gsmini.get_raw_image()
        # print(frame.shape)

        # cv2.imshow("tst", frame)
        # cv2.waitKey(1)

        # frame = cv2.resize(frame, (int(width), int(height)), interpolation=cv2.INTER_CUBIC)
        cv2.imshow("tst", frame)
        cv2.waitKey(1)
        depth, hm, ImgGrad = itd_cvter.convert(frame)
        plt.imshow(hm, cmap="plasma", vmin=0, vmax=4)
        plt.pause(0.0001)

        print("FPS: %.2f" % (1 / (time.time() - tic)))
except KeyboardInterrupt:
    pass
