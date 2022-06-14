import cv2
import numpy as np
from calibrate_digit import takeimg, fishye_calib, imgborder
import pickle

camname = "cam"
takeimg("digiteye/"+camname, 0, 0, "1tst")
para = pickle.load(open("cam2/cam2_calib.pkl", "rb"))
img = cv2.imread("/home/jhz/桌面/gelsight_resconstruct/gelsight-main/digiteye/cam/1tst.jpg")
border = imgborder(img, 1, campara=para)
print(border)
