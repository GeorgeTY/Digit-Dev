import cv2
import csv
import time
import socket
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import ndimage as ndi
import img_to_depth_digit as itd


MethodChoose = 2
host = "127.0.0.1"
port = 6319

width, height = 640, 480
width_splitter, height_splitter = 640 / 4, 480 / 3
itd_cvter = itd.ImageToDepth(
    "/home/jiangxin/ATISensor/digit-main/digiteye/calibrate_D20299_0504_2"
)

sudo_password = "hitsz666"
command = "./simple_test enp0s31f6"  # Command to Run Simple_test
command = command.split()

width_Distribution = np.arange(0, 640 + 1, width_splitter, dtype=int)
height_Distribution = np.arange(0, 480 + 1, height_splitter, dtype=int)
width_Distribution[-1] = width - 1
height_Distribution[-1] = height - 1


def main():
    # Starting Server
    cmd1 = subprocess.Popen(["echo", sudo_password], stdout=subprocess.PIPE)
    cmd2 = subprocess.Popen(
        ["sudo", "-S"] + command, stdin=cmd1.stdout, stdout=subprocess.PIPE
    )
    # output = cmd2.stdout.read().decode()

    video1 = cv2.VideoCapture(0)

    time.sleep(1)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create an object
    client.connect((host, port))  # Now connect to the server

    response = client.recv(4096).decode().rstrip("\x00")  # Receive From Server
    print("Received: %s" % response)
    if response == "OPGT":
        print("Operational-Got")
    elif response == "OPFL":
        print("Operational-Fail")
        print("Exiting")
        exit()

    timeout = time.time() + 2
    while time.time() < timeout:
        ret, frame = video1.read()

    frame = cv2.resize(frame, (int(width), int(height)), interpolation=cv2.INTER_CUBIC)
    depth, hm_clb, ImgGrad = itd_cvter.convert(frame)

    plt.ion()
    if MethodChoose == 1:

        alpha = 0.6  # For Center Measurement
        beta = 0.5  # For Mean Measurement
    elif MethodChoose == 2:
        alpha = 3  # For Center Measurement
        beta = 0.5  # For Mean Measurement

    while True:
        tic = time.time()
        ret, frame = video1.read()
        frame = cv2.resize(
            frame, (int(width), int(height)), interpolation=cv2.INTER_CUBIC
        )
        depth, hm, ImgGrad = itd_cvter.convert(frame)

        ### Method 1: Mean Measurement ###
        if MethodChoose == 1:

            hm_roi_alpha = np.where(
                hm - hm_clb * alpha > 0, hm, 0
            )  ## For Center Measurement
            center = ndi.center_of_mass(hm_roi_alpha)

            hm_roi_beta = np.where(
                hm - hm_clb * beta > 0, hm, 0
            )  ## For Mean Measurement

            plt.clf()
            plt.imshow(hm_roi_beta, cmap="plasma", vmin=0, vmax=4)
            plt.colorbar()
            plt.scatter(center[1], center[0])
            plt.pause(0.01)
            toc = time.time()
            mean_hm_roi = np.mean(hm_roi_beta)
            print(
                "FPS: %.2f" % (1 / (toc - tic)),
                "Area: ",
                int(center[1] / width_splitter),
                int(center[0] / height_splitter),
                "Beta-Mean: %.5f" % mean_hm_roi,
                "Sum: %.5f" % np.sum(hm_roi_beta),
            )
            cv2.imshow("Digit View", frame)
            key = cv2.waitKey(100)
            if key == ord("s"):  # Press s to save the data
                # Getting Data from sensor
                response = ""
                message = "REQD".encode()
                while response == "":
                    print("Send : %s" % message)
                    client.send(message)  # Send data
                    response = client.recv(4096)
                    print("Received: %s" % response.decode())
                force = response.decode().rstrip("\x00")

                if force != "":
                    with open("output.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(
                            [
                                int(center[1] / width_splitter),
                                int(center[0] / height_splitter),
                                force,
                                mean_hm_roi,
                            ]
                        )
                        print("Wrote to CSV: %s" % force)
            elif key == ord("v"):
                # Getting Data from sensor
                response = ""
                message = "REQD".encode()
                while response == "":
                    print("Send : %s" % message)
                    client.send(message)  # Send data
                    response = client.recv(4096)
                force = response.decode().rstrip("\x00")

                if force != "":
                    print("Preview: %s" % response.decode())

        ### Method 2: Region Measurement ###
        if MethodChoose == 2:

            hm_roi_alpha = np.where(
                hm - hm_clb * alpha > 0, hm, 0
            )  ## For Center Measurement
            center = ndi.center_of_mass(hm_roi_alpha)

            hm_roi_beta = hm[
                height_Distribution[
                    int(center[0] / height_splitter)
                ] : height_Distribution[int(center[0] / height_splitter) + 1],
                width_Distribution[
                    int(center[1] / width_splitter)
                ] : width_Distribution[int(center[1] / width_splitter) + 1],
            ]
            # print(hm_roi_beta.shape, center)

            plt.clf()
            plt.imshow(hm_roi_alpha, cmap="plasma", vmin=0, vmax=4)
            rect = mpatches.Rectangle(
                (
                    width_Distribution[int(center[1] / width_splitter)],
                    height_Distribution[int(center[0] / height_splitter)],
                ),
                width_splitter,
                height_splitter,
                fill=False,
                color="purple",
                linewidth=2,
            )
            plt.gca().add_patch(rect)
            frame = cv2.rectangle(
                frame,
                (
                    width_Distribution[int(center[1] / width_splitter)],
                    height_Distribution[int(center[0] / height_splitter)],
                ),
                (
                    width_Distribution[int(center[1] / width_splitter) + 1],
                    height_Distribution[int(center[0] / height_splitter) + 1],
                ),
                (0, 0, 255),
                2,
            )
            plt.colorbar()
            plt.scatter(center[1], center[0])
            plt.pause(0.01)
            toc = time.time()
            mean_hm_roi = np.mean(hm_roi_beta)
            print(
                "FPS: %.2f" % (1 / (toc - tic)),
                "Area: ",
                int(center[1] / width_splitter),
                int(center[0] / height_splitter),
                "Beta-Mean: %.5f" % mean_hm_roi,
                "Sum: %.5f" % np.sum(hm_roi_beta),
            )
            cv2.imshow("Digit View", frame)
            key = cv2.waitKey(100)
            if key == ord("s"):  # Press s to save the data
                # Getting Data from sensor
                response = ""
                message = "REQD".encode()
                while response == "":
                    print("Send : %s" % message)
                    client.send(message)  # Send data
                    response = client.recv(4096)
                    print("Received: %s" % response.decode())
                force = response.decode().rstrip("\x00")

                if force != "":
                    with open("output.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(
                            [
                                int(center[1] / width_splitter),
                                int(center[0] / height_splitter),
                                force,
                                mean_hm_roi,
                            ]
                        )
                        print("Wrote to CSV: %s" % force)
            elif key == ord("v"):
                # Getting Data from sensor
                response = ""
                message = "REQD".encode()
                while response == "":
                    print("Send : %s" % message)
                    client.send(message)  # Send data
                    response = client.recv(4096)
                force = response.decode().rstrip("\x00")

                if force != "":
                    print("Preview: %s" % response.decode())


if __name__ == "__main__":
    main()
