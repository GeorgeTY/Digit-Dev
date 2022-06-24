import csv
import time
import socket
import subprocess


host = "127.0.0.1"
port = 6319

sudo_password = "hitsz666"
command = "./simple_test enp0s31f6"  # Command to Run Simple_test
command = command.split()


def getchar():
    # Returns a single character from standard input
    import os

    ch = ""
    if os.name == "nt":  # how it works on windows
        import msvcrt

        ch = msvcrt.getch()
    else:
        import tty, termios, sys

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ord(ch) == 3:
        quit()  # handle ctrl+C
    return ch


def main():
    # Starting Server
    cmd1 = subprocess.Popen(["echo", sudo_password], stdout=subprocess.PIPE)
    cmd2 = subprocess.Popen(
        ["sudo", "-S"] + command, stdin=cmd1.stdout, stdout=subprocess.PIPE
    )

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
        cmd1.kill()
        client.close()
        exit()

    i = 0
    while True:
        key = getchar()
        print("You pressed %c (%i)" % (key, ord(key)))
        if key == "v":  ## 118 --> v
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
                i = i + 1
                with open("output.csv", "a") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(
                        [
                            i,
                            force,
                        ]
                    )
                    print("Wrote to CSV: %s" % force)

        if key == "q":
            print("Exiting")
            cmd1.kill()
            client.close()
            exit()


if __name__ == "__main__":
    main()
