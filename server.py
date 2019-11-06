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

print("Waiting for connection on RFCOMM channel %d" % port)
client_sock, client_info = SERVER_SOCK.accept()
print("Accepted connection from ", client_info)

while True:
    data = client_sock.recv(1024)
    if len(data) == 0:
        break
    print("received [%s]" % data)

    # do we need decode?
    stringData = data.decode('utf-8')

    if 'command' in stringData:
        if 'screenshot' in stringData:
            takeScreenshot()
            filePath = Path(DESKTOP_PATH)
            client_sock.send("screenshot.png")
            f = open(filePath, 'r')
            while True:
                content = f.read(1024)
                if len(content) != 0:
                    client_sock.send(content)
                else:
                    break
            f.close()
        elif 'file' in stringData:
            args = stringData.split()
            print(args[1])
            filePath = Path(args[1])
            f = open(filePath, 'r')
            while True:
                content = f.read(1024)
                if len(content) != 0:
                    client_sock.send(content)
                else:
                    break

            f.close()
        elif 'recieve' in stringData:
            # recieve file name
            data = client_sock.recv(1024)
            # f = open("guru99.txt", "w+")
            while True:
                data = client_sock.recv(1024)
                if len(data) == 0:
                    break
                buffer = data.decode('utf-8')
                # f.write(buffer)
            # f.close()
        elif 'stop' in stringData:
            break
        else:
            print("wrong command [%s]" % stringData)

print("disconnected")
client_sock.close()
SERVER_SOCK.close()