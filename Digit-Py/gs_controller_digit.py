import modeling.geometric_model as gm
import visualization.panda.world as wd
import cv2
import other.img_to_depth_digit as itd
import time
import numpy as np
from digit_interface.digit import Digit
from digit_interface.digit_handler import DigitHandler
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
from gelsight import gsdevice

base = wd.World(cam_pos=[0.03, 0.03, 0.07], lookat_pos=[0.015, 0.015, 0])  # 控制实时点云显示

itd_cvter = itd.ImageToDepth(
    "/home/jiangxin/uwu-dev/Digit-Dev/Digit-Py/digiteye/calibrate_gsmini_0329_1"
)


def gsmini_connect():
    dev = gsdevice.Camera(gsdevice.Finger.MINI, dev_id=0)
    dev.connect()
    return dev


gsmini = gsmini_connect()

# video1 = cv2.VideoCapture(0)
# width = int(video1.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(video1.get(cv2.CAP_PROP_FRAME_HEIGHT))
# print(width, height)
pointcloud = None
# width=640
# height=480
plt.ion()

#######################这种方法并不好用#############
# def init_frame():
#     #有marker的弹性体在初始时由于marker会出现误差
#     for i in range(0,15,1):
#         ret, frame = video1.read()
#     ret, first_frame=video1.read()
#     cv2.imshow("tst", first_frame)
#     first_frame = cv2.resize(first_frame, (int(width), int(height)), interpolation=cv2.INTER_CUBIC)
#     first_depth, first_hm ,first_ImgGrad = itd_cvter.convert(first_frame)
#     return first_depth

# first_depth= init_frame()


pcdm = []


def update(gsmini, pcdm, task):
    if len(pcdm) != 0:
        for one_pcdm in pcdm:
            one_pcdm.detach()
    else:
        pcdm.append(None)
    key = cv2.waitKey(1)
    if int(key) == 113:
        # video1.release()
        gsmini.stop_video()
        return task.done
    # ret, frame = video1.read()
    frame = gsmini.get_raw_image()
    # print(frame)
    # frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
    # frame = cv2.imread(
    #     "/home/jiangxin/ATISensor/digit-main/digiteye/calibrate_0113/1.jpg"
    # )

    cv2.imshow("tst", frame)
    # cv2.waitKey(0)

    frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_CUBIC)
    tic = time.time()
    depth, hm, ImgGrad = itd_cvter.convert(frame)
    plt.imshow(hm, cmap="plasma")
    plt.pause(0.01)
    # depth[:,2]=depth[:,2]-first_depth[:,2]

    # if p1.is_alive() == False:
    #     p1.start()
    toc = time.time()
    # print("hm mean: ", hm.mean())
    # print("time cost: ", toc - tic)
    pcdm[0] = gm.GeometricModel(depth * 0.001)
    pcdm[0].attach_to(base)
    return task.again


# q = Queue()
# p1 = Process(target=plt.show, args=())
# p1.start()

taskMgr.doMethodLater(0.01, update, "update", extraArgs=[gsmini, pcdm], appendTask=True)
base.run()
