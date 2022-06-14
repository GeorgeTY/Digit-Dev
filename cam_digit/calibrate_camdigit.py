# 相机标定

import cv2

# 首先读取图像并转为灰度图
img = cv2.imread('/home/jhz/桌面/gelsight_resconstruct/gelsight-main/cam_digit/images/1.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# cv2.imshow("img",img)
# cv2.imshow("gray",gray)

# 使用OpenCV的cv2.findChessboardCorners()函数找出棋盘图中的对角（即图片中黑白相对的点的坐标）,
# 同时使用cv2.drawChessboardCorners()将之画出来

# cv2.findChessboardCorners参数patternSize取（9,5）－－棋盘图中每行和每列交点的个数
# 取（9,5）下面打印corners才会有输出，不然是None,
# 其原因在于导入的图片./camera_cal/calibration1.jpg数一下交点的数目，一行有９个，一列有５个
# Adam博客当中取（9,6）原因在于他的图和我的图不一样，认真数一下可以发现他的图确实是一行９个一列６个角点
# 事实证明，（9,4）也可以，只要size小于图片中的交点数即可

# 函数解析参见官网https://docs.opencv.org/3.3.0/dc/dbb/tutorial_py_calibration.html
# It returns the corner points and retval which will be True if pattern is obtained.
# These corners will be placed in an order (from left-to-right, top-to-bottom)
ret, corners = cv2.findChessboardCorners(gray, (11, 8),None)
print(ret)
print(corners)  # 交点坐标

if ret == True:
    img = cv2.drawChessboardCorners(img, (11, 8), corners, ret)

cv2.imshow("final",img)

cv2.waitKey()
cv2.destroyAllWindows()




#####################################完整的相机标定程序###################################

# import cv2
# import numpy as np

# # 首先读取图像并转为灰度图
# img = cv2.imread('./camera_cal/calibration1.jpg')
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # cv2.imshow("img",img)
# # cv2.imshow("gray",gray)

# # 使用OpenCV的cv2.findChessboardCorners()函数找出棋盘图中的对角（即图片中黑白相对的点的坐标）,
# # 同时使用cv2.drawChessboardCorners()将之画出来

# # cv2.findChessboardCorners参数patternSize取（9,5）－－棋盘图中每行和每列交点的个数
# # 取（9,5）下面打印corners才会有输出，不然是None,
# # 其原因在于导入的图片./camera_cal/calibration1.jpg数一下交点的数目，一行有９个，一列有５个
# # Adam博客当中取（9,6）原因在于他的图和我的图不一样，认真数一下可以发现他的图确实是一行９个一列６个角点
# # 事实证明，（9,4）也可以，只要size小于图片中的交点数即可

# # 函数解析参见官网https://docs.opencv.org/3.3.0/dc/dbb/tutorial_py_calibration.html
# # It returns the corner points and retval which will be True if pattern is obtained.
# # These corners will be placed in an order (from left-to-right, top-to-bottom)
# ret, corners = cv2.findChessboardCorners(gray, (9, 5),None)
# # print(ret)
# # print(corners)  # 交点坐标

# if ret == True:
#     img = cv2.drawChessboardCorners(img, (9, 5), corners, ret)

# cv2.imshow("result",img)

# # 构造这些对角点在在现实世界中的相对位置，我们将这些位置简化成整数值
# objp = np.zeros((5*9, 3), np.float32)
# objp[:, :2] = np.mgrid[0:9, 0:5].T.reshape(-1, 2)

# img_points = []
# obj_points = []

# img_points.append(corners)
# obj_points.append(objp)

# # 最后我们使用OpenCV中的 cv2.calibrateCamera() 即可求得这个相机的畸变系数，在后面的所有图像的矫正都可以使用这一组系数来完成
# image_size = (img.shape[1], img.shape[0])
# #  It returns the camera matrix, distortion coefficients, rotation and translation vectors etc.
# ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points,image_size, None, None)

# test_img = cv2.imread("./camera_cal/calibration3.jpg")
# # 这里cv2.undistort的最后一个参数依旧选用原来的相机矩阵mtx
# # 也可以尝试做opencv官网举例的使用cv2.getOptimalNewCameraMatrix（）基于自由缩放参数来优化相机矩阵，之后再带入
# undist = cv2.undistort(test_img, mtx, dist, None, mtx)

# cv2.imshow("test_img",test_img)
# cv2.imshow("undist",undist)

# cv2.waitKey()
# cv2.destroyAllWindows()
