import sys
import pyautogui
from pathlib import Path, PureWindowsPath
from bluetooth import *
import math

BUFFER_SIZE = 1024
DESKTOP_PATH = os.path.expanduser("~\Desktop\\")
SERVER_SOCK = BluetoothSocket(RFCOMM)
UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

def takeScreenshot():
    myScreenshot = pyautogui.screenshot()
    filePath = DESKTOP_PATH + "screenshot.png"
    print(filePath)
    myScreenshot.save(filePath)
    return

SERVER_SOCK.bind(("", PORT_ANY))
SERVER_SOCK.listen(1)

port = SERVER_SOCK.getsockname()[1]

advertise_service(SERVER_SOCK, "SampleServer",
                      service_id=UUID,
                      service_classes=[UUID, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE])


print(os.path.basename(DESKTOP_PATH))
print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = SERVER_SOCK.accept()
print("Accepted connection from ", client_info)

while True:
    print("Enter command...")
    command = client_sock.recv(1024)
    if len(command) == 0:
        break
    print("received [%s]" % command)

    stringData = command.decode('utf-8')

    if 'command' in stringData:
        if 'recieve' in stringData:
            fileInfo = client_sock.recv(1024)
            fileNameAndSize = fileInfo.decode('utf-8')
            print(fileNameAndSize)

            args = fileNameAndSize.split()
            fileName = args[0]
            size = int(args[1])
            checksum = 0

            f = open(str(DESKTOP_PATH) + str(fileName), "wb")
            i = math.floor(size/BUFFER_SIZE)
            buffi = size - BUFFER_SIZE*i
            data = b''
            while True:
                data = client_sock.recv(BUFFER_SIZE)
                if len(data) == buffi:
                    break
                f.write(data)

            f.write(data)
            f.close()
            print("original size - " + str(args[1]) + " vs revieved size - " + str(checksum))
            print("OK")
        else:
            filePath = ""
            fileSize = 0
            message = ""
            if 'screenshot' in stringData:
                takeScreenshot()
                filePath = DESKTOP_PATH + "screenshot.png"
                fileSize = os.stat(filePath).st_size
                message = "screenshot.png " + str(fileSize)
            elif 'file' in stringData:
                args = stringData.split()
                filePath = str(args[2])
                fileSize = os.stat(filePath).st_size
                fileName = os.path.basename(filePath)
                message = fileName + " " + str(fileSize)

            print("file size - " + str(fileSize))
            client_sock.send(message)

            f = open(filePath, 'rb')
            flag = 0
            while True:
                content = f.read(BUFFER_SIZE)
                if len(content) != 0:
                    flag = client_sock.send(content)
                    print(flag)
                else:
                    break

            print("file sent")
            f.close()

    elif 'stop' in stringData:
        break
    else:
        print("wrong command [%s]" % stringData)

print("disconnected")
client_sock.close()
SERVER_SOCK.close()