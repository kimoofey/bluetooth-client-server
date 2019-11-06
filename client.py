import os
import pyautogui
from bluetooth import *
from pathlib import Path, PureWindowsPath
import sys
import math

BUFFER_SIZE = 1024
DESKTOP_PATH = os.path.expanduser("~\Desktop\\")

def takeScreenshot():
    myScreenshot = pyautogui.screenshot()
    filePath = DESKTOP_PATH + "screenshot.png"
    print(filePath)
    myScreenshot.save(filePath)
    return

addr = "18:CF:5E:E4:AC:A7"

#if len(sys.argv) < 2:
#    print("no device specified.  Searching all nearby bluetooth devices for")
#    print("the SampleServer service")
#else:
#addr = sys.argv[1]
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
    command = input()
    if len(command) == 0:
        break

    sock.send(command)

    # command screenshot
    # command file
    # command recieve file
    # command recieve screenshot
    # stop

    if 'command' in command:
        if 'recieve' in command:
            filePath = ""
            fileSize = 0
            message = ""
            if 'screenshot' in command:
                takeScreenshot()
                filePath = DESKTOP_PATH + "screenshot.png"
                fileSize = os.stat(filePath).st_size
                message = "screenshot.png " + str(fileSize)
            elif 'file' in command:
                args = command.split()
                filePath = str(args[3])
                fileSize = os.stat(filePath).st_size
                message = os.path.basename(filePath) + " " + str(fileSize)

            print(fileSize)
            sock.send(message)

            f = open(filePath, 'rb')
            flag = 0
            while True:
                content = f.read(BUFFER_SIZE)
                if len(content) != 0:
                    flag = sock.send(content)
                else:
                    break

            f.close()
        elif 'screenshot' in command or 'file' in command:
            fileInfo = sock.recv(BUFFER_SIZE)
            fileNameAndSize = fileInfo.decode('utf-8')
            print(fileNameAndSize)

            args = fileNameAndSize.split()
            fileName = args[0]
            size = int(args[1])
            checksum = 0
            data = b''
            f = open(str(DESKTOP_PATH) + str(fileName), "wb")
            i = math.floor(size/BUFFER_SIZE)
            buffi = size - BUFFER_SIZE * i
            print(buffi)
            while True:
                data = sock.recv(BUFFER_SIZE)
                if len(data) == buffi:
                    break
                f.write(data)
            f.write(data)
            f.close()
            #print("original size - " + str(args[1]) + " vs revieved size - " + str(checksum))
            print("OK")
    elif 'stop' in command:
        break
    else:
        continue

sock.close()