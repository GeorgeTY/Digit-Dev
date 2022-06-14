from pickle import encode_long
from time import monotonic
import cv2 
import numpy as np
import matplotlib.pyplot as plt
from numpy.core.function_base import linspace
import img_to_depth_digit as itd
from numpy import diff
from PIL import Image
from pylab import  *
import math


def nothing(x):
    pass

def moving_average(interval, window_size):
    window = np.ones(int(window_size)) / float(window_size)
    # print("windsow size:",window)
    return np.convolve(interval, window, 'same')  # numpy的卷积函数

video1 = cv2.VideoCapture(0)
width = (int(video1.get(cv2.CAP_PROP_FRAME_WIDTH)))
height = (int(video1.get(cv2.CAP_PROP_FRAME_HEIGHT)))

itd_cvter = itd.ImageToDepth("digiteye/calibrate_new")

cv2.namedWindow("y_height")    #原始图像

threshold=195
max_threshold=255
cv2.namedWindow("binary")    #原始图像
cv2.namedWindow("frame")    #原始图像

cv2.createTrackbar("threshold","y_height", threshold,max_threshold,nothing)

while True:
    ret, frame_ = video1.read()
    depth, hm ,ImgGrad= itd_cvter.convert(frame_)
        # print(hm)
    hm=2*hm
    if hm.mean()>0.1:   #当按下传感器时才进行处理
        window_size_=10
        x_len=hm.shape[1]
        x=[]
        x_=[]
        y=[]
        y_=[]
        y_height_smooth=[]
        print(hm.shape)
        for i in np.linspace(0,hm.shape[0]-1,hm.shape[0]):
            # print(i)
            which_line=int(i)

            # print(which_line)
            y_height=hm[which_line,:]
            # print(y_height)
            y_height=y_height.reshape(x_len,)
            y_height_smooth.append(moving_average(interval=y_height,window_size=window_size_))
            y.append(which_line)
            y_.append(which_line)
            
            x.append(np.argmax(y_height_smooth))
            
            dx=1
            dy=diff(y_height_smooth)/dx
            x_.append(np.argmax(dy))

            # print(np.argmax(dy))

        y_height_smooth=mat(y_height_smooth)
        min_height=y_height_smooth.min()
        max_height=y_height_smooth.max()
        # print(min_height)
        y_height_smooth=cv2.convertScaleAbs(y_height_smooth,alpha=(255/(max_height-min_height)))
        # print(y_height_smooth.shape)
        y_height_smooth=y_height_smooth.reshape(y_height_smooth.shape[0],y_height_smooth.shape[1],1)
        # print(y_height_smooth.shape)
        y_height_smooth=y_height_smooth*5
        y_height_smooth=mat(y_height_smooth)
        cv2.imshow("y_height",y_height_smooth)



        threshold=cv2.getTrackbarPos('threshold',"y_height")
        ret,binary = cv2.threshold(y_height_smooth,threshold,threshold,cv2.THRESH_BINARY)
        cv2.imshow("binary",binary)
        contours, hierarchy=cv2.findContours(image=binary,mode=cv2.RETR_LIST,method=cv2.CHAIN_APPROX_NONE) #函数返回两个值，一个是轮廓本身，还有一个是每条轮廓对应的属性。
        cv2.drawContours(frame_,contours,-1,(0,0,255),2)  
        cv2.imshow("frame",frame_)
        for i in np.linspace(0,np.size(contours)-1,np.size(contours)):
            if np.size(contours[int(i)])>10:
                ellipse = cv2.fitEllipse(contours[int(i)])
                ###print(ellipse
                ###比较一下椭圆的长轴短轴相对长度
                ###draw circle at center
                (xc,yc),(d1,d2),angle = ellipse
                if min(d1,d2)>30: #如果短轴过短 不对该椭圆拟合直线
                    if  max(d1,d2)/min(d1,d2)>1.5:
                        # cv2.circle(frame, (int(xc),int(yc)), 10, (255, 255, 255), -1)
                        # draw vertical line
                        # compute major radius
                        rmajor = max(d1,d2)/2
                        if angle > 90:
                            angle = angle - 90
                        else:
                            angle = angle + 90
                        print(angle)
                        xtop = xc + math.cos(math.radians(angle))*rmajor
                        ytop = yc + math.sin(math.radians(angle))*rmajor
                        xbot = xc + math.cos(math.radians(angle+180))*rmajor
                        ybot = yc + math.sin(math.radians(angle+180))*rmajor
                        cv2.line(frame_, (int(xtop),int(ytop)), (int(xbot),int(ybot)), (255, 255, 255), 2)
                    # image = cv2.line(frame, start_point, end_point, (255,255,255), 2)
                tuoyuan=cv2.ellipse(frame_, ellipse,(255,0,0), 3)
        cv2.imshow("tuoyuan",tuoyuan)

    if cv2.waitKey(1)==25:
        break

cv2.waitKwy(0)