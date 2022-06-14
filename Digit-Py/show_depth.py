import cv2
import img_to_depth_digit as itd
import time
import matplotlib.pyplot as plt


itd_cvter = itd.ImageToDepth(
    "/home/jiangxin/ATISensor/digit-main/digiteye/calibrate_D20299_0504_2"
)


video1 = cv2.VideoCapture(0)
width = int(video1.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video1.get(cv2.CAP_PROP_FRAME_HEIGHT))
# width=640
# height=480
plt.ion()

while True:
    tic = time.time()

    plt.cla()
    ret, frame = video1.read()

    # cv2.imshow("tst", frame)
    # cv2.waitKey(1)

    frame = cv2.resize(frame, (int(width), int(height)), interpolation=cv2.INTER_CUBIC)
    depth, hm, ImgGrad = itd_cvter.convert(frame)
    plt.imshow(hm, cmap="plasma", vmin=0, vmax=4)
    plt.pause(0.0001)

    print("FPS: %.2f" % (1 / (time.time() - tic)))
