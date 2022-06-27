import cv2
import pickle
import numpy as np
import math
import os
from digit_interface.digit import Digit
from digit_interface.digit_handler import DigitHandler
import pprint

# def fishye_calib(img, para):
#     K, D, DIM = para
#     map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
#     undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
#     return undistorted_img


def fishye_calib(img, para):  # 不进行校正
    undistorted_img = img
    return undistorted_img


def iniFrame(frame0):  # 降噪处理？
    ksize = 50 * 2
    sigma = 50

    f0 = cv2.GaussianBlur(frame0, (99, 99), sigma)
    height, width = frame0.shape[:2]

    frame_ = np.asfarray(frame0, float)
    dI = np.mean(f0 - frame_, 2)

    for i in range(0, height):
        for j in range(0, width):
            if dI[i, j] < 5:
                f0[i, j, 0] = f0[i, j, 0] * 0.15 + frame_[i, j, 0] * 0.85
                f0[i, j, 1] = f0[i, j, 1] * 0.15 + frame_[i, j, 1] * 0.85
                f0[i, j, 2] = f0[i, j, 2] * 0.15 + frame_[i, j, 2] * 0.85

    return f0


def evalueCircle(center, radius, width, I, mask):
    [size1, size2] = np.shape(I)
    xq, yq = np.meshgrid(np.arange(size2), np.arange(size1))
    xq = xq - center[0]
    yq = yq - center[1]
    rq = xq * xq + yq * yq

    r2 = radius * radius
    r3 = (radius + width) * (radius + width)
    r1 = r2 * 0.57
    r0 = r2

    m1 = (rq < r0) & (rq > r1)
    m2 = (rq > r2) & (rq < r3)

    m10 = I[(m1 & mask) == 1]
    m20 = I[(m2 & mask) == 1]

    Strongness = np.mean(m10)
    DiffScore = np.mean(m20) - Strongness

    return DiffScore, Strongness


def loopRadius(centerx, centery, I, mask, width, r0, rstep, rrange):
    r = r0
    currentScore, t = evalueCircle([centerx, centery], r0, width, I, mask)
    s1, t = evalueCircle([centerx, centery], r - rstep, width, I, mask)
    s2, t = evalueCircle([centerx, centery], r + rstep, width, I, mask)
    isFound = 0
    if s1 > currentScore and s1 > s2:
        r = r - rstep
        while r > rrange[0]:
            s2, t = evalueCircle([centerx, centery], r - rstep, width, I, mask)
            if s2 < s1:
                isFound = 1
                R = r
                maxScore = s1
                break
            else:
                s1 = s2
                r = r - rstep
    elif s1 < s2 and s2 > currentScore:
        r = r + rstep
        while r <= rrange[1]:
            s1, t = evalueCircle([centerx, centery], r + rstep, width, I, mask)
            if s2 > s1:
                isFound = 1
                R = r
                maxScore = s2
                break
            else:
                s2 = s1
                r = r + rstep
    else:
        isFound = 1
        R = r0
        maxScore = currentScore

    if not isFound:
        R = 0
        maxScore = 0

    return R, maxScore


def digit_connect():
    # Print a list of connected DIGIT's
    digits = DigitHandler.list_digits()
    print("Connected DIGIT's to Host:")
    pprint.pprint(digits)
    print(digits[0]["serial"])
    digit = Digit(digits[0]["serial"], "Right Gripper")
    digit.connect()
    print(digit.info())

    intensity = 15
    # red=(intensity,0,0)
    # green=(0,intensity,0)
    # blue=(0,0,intensity)
    rgb = (intensity, intensity, intensity)
    light_color = rgb
    digit.set_intensity_rgb(*light_color)

    vga_res = Digit.STREAMS["VGA"]
    digit.set_resolution(vga_res)
    # Change DIGIT FPS to 15fps
    fps_15 = Digit.STREAMS["VGA"]["fps"]["15fps"]
    digit.set_fps(fps_15)
    return digit


digit_R = digit_connect()


def loopcenter(centerx, centery, cstep, I, mask, rwidth, r0, rstep, rrange):
    LoopFlag = 1
    centerx0 = centerx
    centery0 = centery
    R0, CurrentScore = loopRadius(centerx, centery, I, mask, rwidth, r0, rstep, rrange)

    while LoopFlag:
        LoopFlag = 0
        R1, score1 = loopRadius(
            centerx0 + cstep, centery0, I, mask, rwidth, r0, rstep, rrange
        )
        R2, score2 = loopRadius(
            centerx0 - cstep, centery0, I, mask, rwidth, r0, rstep, rrange
        )
        if score1 > CurrentScore and score1 > score2:
            LoopFlag = 1
            while score1 > CurrentScore:
                CurrentScore = score1
                centerx0 = centerx0 + cstep
                R0 = R1
                R1, score1 = loopRadius(
                    centerx0 + cstep, centery0, I, mask, rwidth, r0, rstep, rrange
                )
        elif score2 > CurrentScore:
            LoopFlag = 1
            while score2 > CurrentScore:
                CurrentScore = score2
                centerx0 = centerx0 - cstep
                R0 = R2
                R2, score2 = loopRadius(
                    centerx0 - cstep, centery0, I, mask, rwidth, r0, rstep, rrange
                )

        R1, score1 = loopRadius(
            centerx0, centery0 + cstep, I, mask, rwidth, r0, rstep, rrange
        )
        R2, score2 = loopRadius(
            centerx0, centery0 - cstep, I, mask, rwidth, r0, rstep, rrange
        )

        if score1 > CurrentScore and score1 > score2:
            LoopFlag = 1
            while score1 > CurrentScore:
                CurrentScore = score1
                centery0 = centery0 + cstep
                R0 = R1
                R1, score1 = loopRadius(
                    centerx0, centery0 + cstep, I, mask, rwidth, r0, rstep, rrange
                )
        elif score2 > CurrentScore and score1 < score2:
            LoopFlag = 1
            while score2 > CurrentScore and score1 < score2:
                CurrentScore = score2
                centery0 = centery0 - cstep
                R0 = R2
                R2, score2 = loopRadius(
                    centerx0, centery0 - cstep, I, mask, rwidth, r0, rstep, rrange
                )

    ResCenter = [centerx0, centery0]
    ResRadius = R0
    return ResCenter, ResRadius


def LookuptableFromBall_Bnz(
    dI,
    f0,
    bins,
    center,
    BallRad,
    Pixmm,
    validmask,
    graddir=None,
    countmap=None,
    gradmag=None,
    zeropoint=None,
    lookscale=None,
    f01=None,
):
    #   center:[x,y]

    BallRad = BallRad / Pixmm  # in pix
    print("BallRad:", BallRad)

    #   para ini
    if zeropoint is None:
        zeropoint = -90
    if lookscale is None:
        lookscale = 180
    if f01 is None:
        t = np.mean(f0)
        f01 = 1 + ((t / f0) - 1) * 2

    sizey = np.size(dI, 0)
    sizex = np.size(dI, 1)
    validid = np.flatnonzero(validmask)
    tmp = np.size(validmask, 1)
    y = validid // tmp
    x = validid % tmp
    yvalid = y - center[1]
    xvalid = x - center[0]
    rvalid = np.sqrt(xvalid * xvalid + yvalid * yvalid)
    if np.amax(rvalid - BallRad) > 0:
        print("Contact Radius is too large. Ignoring the exceeding area")
        rvalid[rvalid > BallRad] = BallRad - 0.001

    gradxseq = np.arcsin(rvalid / BallRad)
    gradyseq = np.arctan2(-yvalid, -xvalid)

    binm = bins - 1
    sizet = sizex * sizey
    sizet2 = sizet * 2

    r1 = dI[y[:], x[:], 0] * f01[y[:], x[:], 0]
    g1 = dI[y[:], x[:], 1] * f01[y[:], x[:], 1]
    b1 = dI[y[:], x[:], 2] * f01[y[:], x[:], 2]
    r2 = (r1 - zeropoint) / lookscale
    r2[r2 < 0] = 0
    r2[r2 > 1] = 1

    g2 = (g1 - zeropoint) / lookscale
    g2[g2 < 0] = 0
    g2[g2 > 1] = 1

    b2 = (b1 - zeropoint) / lookscale
    b2[b2 < 0] = 0
    b2[b2 > 1] = 1

    r3 = (np.floor(r2 * binm)).astype(int)
    g3 = (np.floor(g2 * binm)).astype(int)
    b3 = (np.floor(b2 * binm)).astype(int)

    if gradmag is None:
        gradmag = np.zeros((bins, bins, bins))
        countmap = np.zeros((bins, bins, bins))
        graddir = np.zeros((bins, bins, bins))

    for i in range(0, len(r1)):
        t1 = countmap[r3[i], g3[i], b3[i]]
        countmap[r3[i], g3[i], b3[i]] = countmap[r3[i], g3[i], b3[i]] + 1
        if t1:
            gradmag[r3[i], g3[i], b3[i]] = (
                gradmag[r3[i], g3[i], b3[i]] * t1 + gradxseq[i]
            ) / (t1 + 1)
            a1 = graddir[r3[i], g3[i], b3[i]]
            a2 = gradyseq[i]
            if a2 - a1 > math.pi:
                a2 = a2 - math.pi * 2
            elif a1 - a2 > math.pi:
                a2 = a2 + math.pi * 2

            graddir[r3[i], g3[i], b3[i]] = (a1 * t1 + a2) / (t1 + 1)

        else:
            gradmag[r3[i], g3[i], b3[i]] = gradxseq[i]
            graddir[r3[i], g3[i], b3[i]] = gradyseq[i]

    return gradmag, graddir, countmap


def on_Mouse(event, x, y, flags, param):
    global mouseX, mouseY, mouseCount
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseX, mouseY = x, y
        mouseCount += 1
        print("Mouse clicked at:", mouseX, mouseY)
        print("mouseCount: ", mouseCount)


def FindBallArea_coarse_m(I, frame=None, MANUAL=None):
    global mouseX, mouseY, mouseCount
    TEST_DISPLAY = 0
    if frame is None:
        frame[:, :, 0] = (I + 50) * 1.5
        frame[:, :, 1] = (I + 50) * 1.5
        frame[:, :, 2] = (I + 50) * 1.5

    MarkerAreaThresh = 15
    SE = np.ones((7, 7))
    RadiusRange = [40, 500]
    RadiusTestWidth = 50

    size1, size2 = np.shape(I)
    mask1 = (I > MarkerAreaThresh).astype("uint8")
    # mask1 = np.uint8(mask1)
    # cv2.imwrite("mask1.jpg", mask1)
    mask2 = (cv2.dilate(mask1, SE, iterations=1) < 1).astype("uint8")
    I_ = I * mask2

    thresh = 0.35
    sumcol = np.sum(I_, 0)
    sumcol0 = sumcol - np.max(sumcol)
    t = np.flatnonzero(sumcol0 < np.min(sumcol0) * thresh)

    center1X = (t[0] + t[len(t) - 1]) / 2
    Radius1 = (t[len(t) - 1] - t[0]) / 2

    sumrow = np.sum(I_, 1)
    sumrow0 = sumrow - np.max(sumrow)
    t = np.flatnonzero(sumrow0 < np.min(sumrow0) * thresh)
    center1Y = (t[0] + t[len(t) - 1]) / 2

    stepradius = 2
    stepCenter = 2

    print(center1X, center1Y, Radius1)

    center, Radius = loopcenter(
        center1X,
        center1Y,
        stepCenter * 2,
        I_,
        mask2,
        RadiusTestWidth,
        Radius1,
        stepradius * 2,
        RadiusRange,
    )
    center, Radius = loopcenter(
        center[0],
        center[1],
        stepCenter,
        I_,
        mask2,
        RadiusTestWidth,
        Radius,
        stepradius,
        RadiusRange,
    )

    Radius = Radius - 3

    if TEST_DISPLAY:
        xq, yq = np.meshgrid(np.arange(size2), np.arange(size1))
        xq = xq - center[0]
        yq = yq - center[1]
        rq = xq * xq + yq * yq
        displayIm = np.zeros([size1, size2, 3])
        displayIm[:, :, 0] = -I_ / 150
        displayIm[:, :, 1] = (rq < (Radius * Radius)) / 2.5
        cv2.imshow("tst", displayIm)

    if MANUAL:
        kstep = 2
        Radius1 = Radius

        m, n = np.shape(frame)[:2]
        disIm = np.zeros((m, n, 3)).astype("uint8")
        disIm[:, :, :] = frame[:, :, :]  # Unit8?
        # print(disIm)

        xq, yq = np.meshgrid(np.arange(size2), np.arange(size1))
        BallBord = [
            center[0] - Radius1,
            center[0] + Radius1,
            center[1] - Radius1,
            center[1] + Radius1,
        ]
        rq = (xq - center[0]) * (xq - center[0]) + (yq - center[1]) * (yq - center[1])
        r2 = Radius1 * Radius1

        a = np.zeros((m, n)).astype(int)
        a[:, :] = frame[:, :, 0]
        # a[rq < r2] = a[rq < r2] - 100
        disIm[:, :, 0] = a
        cv2.namedWindow("tst")
        cv2.setMouseCallback("tst", on_Mouse)
        h, w = disIm.shape[:2]
        size = (int(w * 2), int(h * 2))
        img = cv2.resize(disIm, size, interpolation=cv2.INTER_AREA)
        o_img = img.copy()
        gotMouse = False
        while True:
            cv2.imshow("tst", img)
            # print("inloop: ", mouseCount)
            if mouseCount == 1:
                mouseX1, mouseY1 = mouseX, mouseY
                img = o_img.copy()
                # print("mouse1")
            elif mouseCount == 2:
                mouseX2, mouseY2 = mouseX, mouseY
                gotMouse = True
                print("mouse2")
                mouseCount = 0
                center[0], center[1] = (mouseX1 + mouseX2) / 4, (mouseY1 + mouseY2) / 4
                Radius1 = (
                    np.sqrt(
                        (mouseX1 - mouseX2) * (mouseX1 - mouseX2)
                        + (mouseY1 - mouseY2) * (mouseY1 - mouseY2)
                    )
                    / 4
                )
                r2 = Radius1 * Radius1
                # print(center, Radius1)
                addimg = img.copy()
                cv2.circle(
                    addimg,
                    ((mouseX1 + mouseX2) // 2, (mouseY1 + mouseY2) // 2),
                    int(
                        np.sqrt((mouseX1 - mouseX2) ** 2 + (mouseY1 - mouseY2) ** 2) / 2
                    ),
                    (0, 0, 255),
                    -1,
                )
                cv2.line(
                    addimg,
                    (mouseX1, mouseY1),
                    (mouseX2, mouseY2),
                    (47, 242, 79),
                )
                alpha = 0.05
                img = cv2.addWeighted(addimg, alpha, img, 1 - alpha, 0)
            # cv2.imshow("tst", disIm)
            # print("Press 'a' 'd' 'w' 's' to adjust the circle.\nPress SPACE to exit.")

            # key = cv2.waitKey(0)
            # if key & 0xFF == 32 and mouseCount == 0:
            #     print("Got the mask.")
            #     print("center:", center, "Radius:", Radius1)
            #     break
            k = cv2.waitKey(20) & 0xFF
            if k == 32 and mouseCount == 0 and gotMouse:
                print("Got the mask.")
                print("center:", center, "Radius:", Radius1)
                break

            # elif key & 0xFF == ord("w"):
            #     center[1] = center[1] - kstep
            # elif key & 0xFF == ord("s"):
            #     center[1] = center[1] + kstep
            # elif key & 0xFF == ord("a"):
            #     center[0] = center[0] - kstep
            # elif key & 0xFF == ord("d"):
            #     center[0] = center[0] + kstep
            # elif key & 0xFF == ord("-"):
            #     Radius1 = Radius1 - kstep
            #     r2 = Radius1 * Radius1
            # elif key & 0xFF == ord("="):
            #     Radius1 = Radius1 + kstep
            #     r2 = Radius1 * Radius1

            # BallBord = [center[0] - Radius1, center[0] + Radius1, center[1] - Radius1, center[1] + Radius1]

            #   redraw the circle
            rq = (xq - center[0]) * (xq - center[0]) + (yq - center[1]) * (
                yq - center[1]
            )
            #   unit8?
            a[:, :] = frame[:, :, 0]
            a[rq < r2] = a[rq < r2] - 130
            disIm[:, :, 0] = a
        Radius = Radius1
        ContactMask = rq < r2

    xq, yq = np.meshgrid(np.arange(size2), np.arange(size1))

    xq = xq - center[0]
    yq = yq - center[1]
    rq = xq * xq + yq * yq
    ContactMask = rq < (Radius * Radius)
    ValidMap = mask2

    return ContactMask, ValidMap, center, Radius


def FindBallArea_coarse(I, frame=None, MANUAL=None):

    TEST_DISPLAY = 0
    if frame is None:
        frame[:, :, 0] = (I + 50) * 1.5
        frame[:, :, 1] = (I + 50) * 1.5
        frame[:, :, 2] = (I + 50) * 1.5

    MarkerAreaThresh = 15
    SE = np.ones((7, 7))
    RadiusRange = [40, 500]
    RadiusTestWidth = 50

    size1, size2 = np.shape(I)
    mask1 = (I > MarkerAreaThresh).astype("uint8")
    # mask1 = np.uint8(mask1)
    # cv2.imwrite("mask1.jpg", mask1)
    mask2 = (cv2.dilate(mask1, SE, iterations=1) < 1).astype("uint8")
    I_ = I * mask2

    thresh = 0.35
    sumcol = np.sum(I_, 0)
    sumcol0 = sumcol - np.max(sumcol)
    t = np.flatnonzero(sumcol0 < np.min(sumcol0) * thresh)

    center1X = (t[0] + t[len(t) - 1]) / 2
    Radius1 = (t[len(t) - 1] - t[0]) / 2

    sumrow = np.sum(I_, 1)
    sumrow0 = sumrow - np.max(sumrow)
    t = np.flatnonzero(sumrow0 < np.min(sumrow0) * thresh)
    center1Y = (t[0] + t[len(t) - 1]) / 2

    stepradius = 2
    stepCenter = 2

    print(center1X, center1Y, Radius1)

    center, Radius = loopcenter(
        center1X,
        center1Y,
        stepCenter * 2,
        I_,
        mask2,
        RadiusTestWidth,
        Radius1,
        stepradius * 2,
        RadiusRange,
    )
    center, Radius = loopcenter(
        center[0],
        center[1],
        stepCenter,
        I_,
        mask2,
        RadiusTestWidth,
        Radius,
        stepradius,
        RadiusRange,
    )

    Radius = Radius - 3

    if TEST_DISPLAY:
        xq, yq = np.meshgrid(np.arange(size2), np.arange(size1))
        xq = xq - center[0]
        yq = yq - center[1]
        rq = xq * xq + yq * yq
        displayIm = np.zeros([size1, size2, 3])
        displayIm[:, :, 0] = -I_ / 150
        displayIm[:, :, 1] = (rq < (Radius * Radius)) / 2.5
        cv2.imshow("tst", displayIm)

    if MANUAL:
        kstep = 2
        Radius1 = Radius

        m, n = np.shape(frame)[:2]
        disIm = np.zeros((m, n, 3)).astype("uint8")
        disIm[:, :, :] = frame[:, :, :]  # Unit8?
        # print(disIm)

        xq, yq = np.meshgrid(np.arange(size2), np.arange(size1))
        BallBord = [
            center[0] - Radius1,
            center[0] + Radius1,
            center[1] - Radius1,
            center[1] + Radius1,
        ]
        rq = (xq - center[0]) * (xq - center[0]) + (yq - center[1]) * (yq - center[1])
        r2 = Radius1 * Radius1

        a = np.zeros((m, n)).astype(int)
        a[:, :] = frame[:, :, 0]
        a[rq < r2] = a[rq < r2] - 100
        disIm[:, :, 0] = a

        while True:
            h, w = disIm.shape[:2]
            size = (int(w * 2), int(h * 2))
            img = cv2.resize(disIm, size, interpolation=cv2.INTER_AREA)
            cv2.imshow("tst", img)

            # cv2.imshow("tst", disIm)
            # print("Press 'a' 'd' 'w' 's' to adjust the circle.\nPress SPACE to exit.")
            print("center:", center, "Radius1:", Radius1)
            key = cv2.waitKey(0)
            if key & 0xFF == 32:
                print("Got the mask.")
                break
            elif key & 0xFF == ord("w"):
                center[1] = center[1] - kstep
            elif key & 0xFF == ord("s"):
                center[1] = center[1] + kstep
            elif key & 0xFF == ord("a"):
                center[0] = center[0] - kstep
            elif key & 0xFF == ord("d"):
                center[0] = center[0] + kstep
            elif key & 0xFF == ord("-"):
                Radius1 = Radius1 - kstep
                r2 = Radius1 * Radius1
            elif key & 0xFF == ord("="):
                Radius1 = Radius1 + kstep
                r2 = Radius1 * Radius1

            # BallBord = [center[0] - Radius1, center[0] + Radius1, center[1] - Radius1, center[1] + Radius1]

            #   redraw the circle
            rq = (xq - center[0]) * (xq - center[0]) + (yq - center[1]) * (
                yq - center[1]
            )
            #   unit8?
            a[:, :] = frame[:, :, 0]
            a[rq < r2] = a[rq < r2] - 130
            disIm[:, :, 0] = a
        Radius = Radius1
        ContactMask = rq < r2

    xq, yq = np.meshgrid(np.arange(size2), np.arange(size1))

    xq = xq - center[0]
    yq = yq - center[1]
    rq = xq * xq + yq * yq
    ContactMask = rq < (Radius * Radius)
    ValidMap = mask2

    return ContactMask, ValidMap, center, Radius


def LookuptableSmooth(bins, gradx, grady, countmap):
    if not (countmap[0, 0, 0]):
        countmap[0, 0, 0] = 1
        gradx[0, 0, 0] = 0
        grady[0, 0, 0] = 0

    validid = np.flatnonzero(countmap)
    if len(validid) == bins * bins * bins:
        gradxout0 = gradx
        gradyout0 = grady
        return
    # xout, yout, zout = np.meshgrid(np.arange(bins), np.arange(bins), np.arange(bins))

    # NEED TO CONSIDER THE
    # Method: get the current value to the nearest

    # st = time.time()

    gradxout0 = gradx
    gradyout0 = grady
    invalidid = np.flatnonzero(countmap == 0)

    xvalid = validid // bins % bins
    yvalid = validid // bins // bins
    zvalid = validid % bins

    xinvalid = invalidid // bins % bins
    yinvalid = invalidid // bins // bins
    zinvalid = invalidid % bins

    # print(time.time() - st)
    # st = time.time()
    # print(f"hafjkhfkahksd{len(invalidid)}")

    for i in range(0, len(invalidid)):
        x = xinvalid[i]
        y = yinvalid[i]
        z = zinvalid[i]
        t = (
            (xvalid - x) * (xvalid - x)
            + (yvalid - y) * (yvalid - y)
            + (zvalid - z) * (zvalid - z)
        )
        t2 = np.argmin(t)

        gradxout0[y, x, z] = gradx[yvalid[t2], xvalid[t2], zvalid[t2]]
        gradyout0[y, x, z] = grady[yvalid[t2], xvalid[t2], zvalid[t2]]

    # print(time.time() - st)

    gradxout = gradxout0
    gradyout = gradyout0

    return gradxout, gradyout


def imgborder(frame, fisheyeflag, campara=None):
    if fisheyeflag == 1:
        frame = fishye_calib(frame, campara)
        # cv2.imshow("show", frame)
    m, n = np.shape(frame)[:2]  # m,n frame帧的长，宽
    a = np.zeros((m, n)).astype(int)
    a[:, :] = frame[:, :, 0]  # 取frame的单通道灰度值
    center = np.array([100, 100])
    a1 = 100
    b1 = 100
    kstep = 10
    xq, yq = np.meshgrid(np.arange(n), np.arange(m))  # xq,yq返回像素点坐标
    xqq = xq - center[0]
    yqq = yq - center[1]
    xxq = xqq * xqq
    yyq = yqq * yqq

    disIm = np.zeros((m, n, 3)).astype("uint8")
    disIm[:, :, :] = frame[:, :, :]

    a[xxq < (a1 / 2) * (a1 / 2)] = a[xxq < (a1 / 2) * (a1 / 2)] - 100
    a[yyq < (b1 / 2) * (b1 / 2)] = a[yyq < (b1 / 2) * (b1 / 2)] - 100
    disIm[:, :, 0] = a  # 以center（100，100）为中心，a1,b1为边长，形成了一帧抠图帧，作为窗口使用

    while True:
        h, w = disIm.shape[:2]
        size = (int(w * 1), int(h * 1))
        img = cv2.resize(disIm, size, interpolation=cv2.INTER_AREA)  # 与窗口显示有关
        cv2.imshow("tst", img)
        print("Press 'a' 'd' 'w' 's' to adjust the rectangle.\nPress SPACE to exit.")
        key = cv2.waitKey(0)
        if key & 0xFF == 32:
            print("Got the mask.")
            break
        elif key & 0xFF == ord("w"):
            center[1] = center[1] - kstep
        elif key & 0xFF == ord("s"):
            center[1] = center[1] + kstep
        elif key & 0xFF == ord("a"):
            center[0] = center[0] - kstep
        elif key & 0xFF == ord("d"):
            center[0] = center[0] + kstep
        elif key & 0xFF == ord("-"):
            a1 = a1 - kstep
        elif key & 0xFF == ord("="):
            a1 = a1 + kstep
        elif key & 0xFF == ord("o"):
            b1 = b1 - kstep
        elif key & 0xFF == ord("p"):
            b1 = b1 + kstep

        # BallBord = [center[0] - Radius1, center[0] + Radius1, center[1] - Radius1, center[1] + Radius1]

        #   redraw the circle
        xqq = xq - center[0]
        yqq = yq - center[1]
        xxq = xqq * xqq
        yyq = yqq * yqq
        #   unit8?
        a[:, :] = frame[:, :, 0]
        a[xxq < (a1 / 2) * (a1 / 2)] = a[xxq < (a1 / 2) * (a1 / 2)] - 100
        a[yyq < (b1 / 2) * (b1 / 2)] = a[yyq < (b1 / 2) * (b1 / 2)] - 100
        disIm[:, :, 0] = a

    print("底边长a1: 竖边长b1: 中心坐标： ")  # jhz添加的打印注释
    print(a1, b1, center)
    border = [
        int(center[1] - b1 / 2),
        int(center[1] + b1 / 2),
        int(center[0] - a1 / 2),
        int(center[0] + a1 / 2),
    ]
    print("边界点位置")
    print(border)
    return border


def takeimg(dir, num, camnum=0, filename=None):
    outputfolder = dir + "/"
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)

    # camera = cv2.VideoCapture(camnum)
    # digit_R.get_frame
    i = 0
    while i < num + 1:
        image = digit_R.get_frame(True)

        cv2.imshow("tst", image)
        key = cv2.waitKey(0)
        if key & 0xFF == 32:
            print(i, "done")
            if filename is None:
                cv2.imwrite(outputfolder + str(i) + ".jpg", image)
            else:
                cv2.imwrite(outputfolder + filename + ".jpg", image)

            print("Image size")  # jhz添加，检车图片尺寸
            print(image.shape)
            i = i + 1

    # camera.release()


if __name__ == "__main__":
    # folder = "digiteye/calibrate_ballR2_planeElaster"
    # BallRad = 4 / 2
    folder = "/home/jiangxin/ATISensor/digit-main/digiteye/calibrate_D20299_0504_2"
    # BallRad = 4 / 2
    BallRad = 3 / 2
    mouseX, mouseY, mouseCount = 10, 10, 0

    campara = pickle.load(open("./digiteye/cam/cam2_calib.pkl", "rb"))  # 导入相机的校准参数
    maxcount = 10

    takeimg(folder, maxcount, 0)
    BALL_MANUAL = 1

    READ_RADIUS = 0

    # Pixmm = 10/485*2
    Pixmm = 1 / 35

    bins = 80
    zeropoint = -90
    lookscale = 180

    frame0 = cv2.imread(folder + "/0.jpg")
    border = imgborder(frame0, 1, campara)
    f0 = iniFrame(frame0)
    f0 = f0[border[0] : border[1], border[2] : border[3], :]
    ImList = []
    # border_1 = imgborder(frame0, 1, campara)
    # Pixmm = 25/(border[3] - border[2])

    gradmag = None
    gradir = None
    countmap = None

    a = os.listdir(folder)
    for i in range(1, maxcount + 1):
        f = str(i) + ".jpg"
        img = cv2.imread(folder + "/" + f)
        img = fishye_calib(img, campara)
        ImList.append(img)

    for Frn in range(0, len(ImList)):
        print("Frn:", Frn)
        frame = ImList[Frn]
        height, width = frame.shape[:2]
        frame_ = frame[border[0] : border[1], border[2] : border[3], :]
        I = np.asfarray(frame_, float) - f0
        dI = (np.amin(I, axis=2) - np.amax(I, axis=2)) / 2

        ContactMask, validMask, touchCenter, Radius = FindBallArea_coarse_m(
            dI, frame_, BALL_MANUAL
        )
        # print(
        #     "ContactMask: ",
        #     ContactMask,
        #     "validMask: ",
        #     validMask,
        #     "touchCenter: ",
        #     touchCenter,
        #     "Radius: ",
        #     Radius,
        # )

        validMask = (validMask & ContactMask) > 0
        nomarkermask = (np.amin(-I, axis=2) < 30).astype("uint8")

        kernel = np.ones((5, 5), np.uint8)
        nomarkermask = cv2.erode(nomarkermask, kernel, iterations=1)
        validMask = (validMask & nomarkermask) > 0

        gradmag, gradir, countmap = LookuptableFromBall_Bnz(
            I,
            f0,
            bins,
            touchCenter,
            BallRad,
            Pixmm,
            validMask,
            graddir=gradir,
            countmap=countmap,
            gradmag=gradmag,
            zeropoint=zeropoint,
            lookscale=lookscale,
        )
        print(np.amax(gradmag), np.amin(gradmag))
        print(np.amax(gradir), np.amin(gradir))

    print("Start Calculation")
    GradMag, GradDir = LookuptableSmooth(bins, gradmag, gradir, countmap)
    GradX = -np.cos(GradDir) * GradMag
    GradY = np.sin(GradDir) * GradMag

    result = [
        bins,
        GradMag,
        GradDir,
        GradX,
        GradY,
        zeropoint,
        lookscale,
        Pixmm,
        np.shape(frame),
        border,
    ]

    pickle.dump(result, open(folder + "/Lookuptable.pkl", "wb"))
