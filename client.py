import os
import pyautogui
from bluetooth import *
from pathlib import Path, PureWindowsPath
import sys

DESKTOP_PATH = os.path.expanduser("~\Desktop\\")

def takeScreenshot():
    myScreenshot = pyautogui.screenshot()
    filePath = DESKTOP_PATH + "screenshot.png"
    print(filePath)
    myScreenshot.save(filePath)
    return

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
            if 'screenshot' in command:
                takeScreenshot()
                filePath = Path(DESKTOP_PATH)
                fileSize = os.stat(DESKTOP_PATH).st_size
                print(fileSize)
                message = "screenshot.png " + str(fileSize)
                sock.send(message)

                f = open(filePath, 'rb')
                while True:
                    content = f.read(fileSize)
                    if len(content) != 0:
                        sock.send(content)
                    else:
                        break
                f.close()
                print("file sent")
            elif 'file' in command:
                args = command.split()
                print(args[2])
                filePath = str(Path(args[2]))
                fileSize = os.stat(filePath).st_size
                fileName = os.path.basename(filePath)
                print(fileSize)

                message = fileName + " " + str(fileSize)
                sock.send(message)
                flag = 0

                f = open(filePath, 'rb')
                while True:
                    content = f.read(fileSize)
                    if len(content) != 0:
                        flag = sock.send(content)
                    else:
                        break
                f.close()
                print("sent " + str(flag) + " bytes")
                print("file sent")
        elif 'screenshot' in command or 'file' in command:
            fileInfo = sock.recv(1024)
            filenameAndSize = fileInfo.decode('utf-8')
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
    elif 'stop' in command:
        break
    else:
        continue

sock.close()