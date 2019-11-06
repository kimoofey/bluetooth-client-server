import os
import pyautogui
from bluetooth import *
from pathlib import Path, PureWindowsPath
import sys

DESKTOP_PATH = os.path.expanduser("~\Desktop\\")

addr = None

if len(sys.argv) < 2:
    print("no device specified.  Searching all nearby bluetooth devices for")
    print("the SampleServer service")
else:
    addr = sys.argv[1]
    print("Searching for SampleServer on %s" % addr)

# search for the SampleServer service
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
service_matches = find_service(uuid=uuid, address=addr)

if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \"%s\" on %s" % (name, host))

# Create the client socket
sock = BluetoothSocket(RFCOMM)
sock.connect((host, port))

print("connected.  type stuff")

while True:
    data = input()
    if len(data) == 0:
        break

    sock.send(data)
    command = sock.recv(1024)
    filenameAndSize = command.decode('utf-8')
    print(filenameAndSize)

    args = filenameAndSize.split()
    filename = args[0]
    size = int(args[1])
    checksum = 0

    f = open(str(DESKTOP_PATH) + str(filename), "wb")

    while size > 0:
        if size > 1024:
            data = sock.recv(1024)
            if not len(data) == 1024:
                print("loss of data!")
            size -= 1024
            checksum += 1024
        else:
            data = sock.recv(size)
            checksum += size
            size = 0
        f.write(data)
    f.close()
    print("original size - " + str(args[1]) + " vs revieved size - " + str(checksum))
    print("OK")
sock.close()