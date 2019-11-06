import os
import pyautogui
from pathlib import Path, PureWindowsPath
from bluetooth import *

DESKTOP_PATH = os.path.expanduser("~\Desktop\screenshot.png")
SERVER_SOCK = BluetoothSocket(RFCOMM)
UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

def takeScreenshot():
    myScreenshot = pyautogui.screenshot()
    print(DESKTOP_PATH)
    myScreenshot.save(DESKTOP_PATH)
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
        if 'screenshot' in stringData:
            takeScreenshot()
            filePath = Path(DESKTOP_PATH)
            fileSize = os.stat(DESKTOP_PATH).st_size
            print(fileSize)
            message = "screenshot.png " + str(fileSize)
            client_sock.send(message)

            f = open(filePath, 'rb')
            while True:
                content = f.read(fileSize)
                if len(content) != 0:
                    client_sock.send(content)
                else:
                    break
            f.close()
            print("file sent")
        elif 'file' in stringData:
            args = stringData.split()
            print(args[2])
            filePath = str(Path(args[2]))
            fileSize = os.stat(filePath).st_size
            fileName = os.path.basename(filePath)
            print(fileSize)

            message = fileName + " " + str(fileSize)
            client_sock.send(message)
            f = open(filePath, 'rb')
            flag = 0

            while True:
                content = f.read(fileSize)
                if len(content) != 0:
                    flag = client_sock.send(content)
                else:
                    break
            f.close()
            print("sent " + str(flag) + " bytes")
            print("file sent")
        elif 'recieve' in stringData:
            print("Mockup recieve")
            # # recieve file name
            # data = client_sock.recv(1024)
            # # f = open("guru99.txt", "w+")
            # while True:
            #     data = client_sock.recv(1024)
            #     if len(data) == 0:
            #         break
            #     buffer = data.decode('utf-8')
            #     # f.write(buffer)
            # # f.close()
        elif 'stop' in stringData:
            break
        else:
            print("wrong command [%s]" % stringData)

print("disconnected")
client_sock.close()
SERVER_SOCK.close()