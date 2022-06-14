import socket
from time import sleep
import subprocess


sudo_password = "hitsz666"
command = "./simple_test enp0s31f6"  # Command to Run Simple_test
command = command.split()


host = "127.0.0.1"
port = 6319

cmd1 = subprocess.Popen(["echo", sudo_password], stdout=subprocess.PIPE)
cmd2 = subprocess.Popen(
    ["sudo", "-S"] + command, stdin=cmd1.stdout, stdout=subprocess.PIPE
)

# output = cmd2.stdout.read().decode()

sleep(2)
# print("output:", output)
print("Starting Server")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create an object

client.connect((host, port))  # Now connect to the server
message = ""
response = client.recv(4096)  # Receive should be a power of 2 (not too large)
print("Received: %s" % response.decode())
response_decoded = response.decode().rstrip("\x00")
if response_decoded == "OPGT":
    print("Yes")
elif response_decoded == "OPFL":
    print("Error")
    exit
while True:
    response = ""
    message = "REQD".encode()
    while response == "":
        print("Send : %s" % message)
        sleep(1)
        client.send(message)  # Send data
        response = client.recv(4096)  # Receive should be a power of 2 (not too large)
        print("Received: %s" % response.decode())
