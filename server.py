import pyautogui
from pathlib import Path, PureWindowsPath
from bluetooth import *
import sys
import math

BUFFER_SIZE = 1024
DESKTOP_PATH = os.path.expanduser("~\Desktop\\")
sock = BluetoothSocket(RFCOMM)
UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

def takeScreenshot():
    myScreenshot = pyautogui.screenshot()
    filePath = DESKTOP_PATH + "screenshot.png"
    myScreenshot.save(filePath)
    return

def serverPart():
    sock.bind(("", PORT_ANY))
    sock.listen(1)

    port = sock.getsockname()[1]

    advertise_service(sock, "SampleServer",
                      service_id=UUID,
                      service_classes=[UUID, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE])

    print("Waiting for connection on RFCOMM channel %d" % port)

    serverSock, clientInfo = sock.accept()
    print("Accepted connection from ", clientInfo)

    while True:
        print("Enter command...")
        command = serverSock.recv(1024)
        if len(command) == 0:
            break
        print("received [%s]" % command)

        stringData = command.decode('utf-8')

        if 'command' in stringData:
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
            serverSock.send(message)

            f = open(filePath, 'rb')

            while True:
                content = f.read(BUFFER_SIZE)
                if len(content) != 0:
                    flag = serverSock.send(content)
                    print(flag)
                else:
                    break

            print("File transfered!")
            f.close()

        elif 'stop' in stringData:
            break
        else:
            print("wrong command [%s]" % stringData)

    print("disconnected")
    serverSock.close()
    sock.close()
    return

def clientPart():
    # Implement searching function
    addr = "18:CF:5E:E4:AC:A7"

    # if len(sys.argv) < 2:
    #    print("no device specified.  Searching all nearby bluetooth devices for")
    #    print("the SampleServer service")
    # else:
    # addr = sys.argv[1]
    print("Searching for SampleServer on %s" % addr)

    # search for the SampleServer service
    service_matches = find_service(uuid=UUID, address=addr)

    if len(service_matches) == 0:
        print("couldn't find the SampleServer service =(")
        sys.exit(0)

    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    print("connecting to \"%s\" on %s" % (name, host))

    sock.connect((host, port))

    print("connected.  type stuff")

    while True:
        command = input()
        if len(command) == 0:
            break

        sock.send(command)

        # command screenshot
        # command file
        # stop

        if 'command' in command:
            if 'screenshot' in command or 'file' in command:
                fileInfo = sock.recv(BUFFER_SIZE)
                fileNameAndSize = fileInfo.decode('utf-8')
                print(fileNameAndSize)

                args = fileNameAndSize.split()
                fileName = args[0]
                size = int(args[1])
                
                f = open(str(DESKTOP_PATH) + str(fileName), "wb")
                buffi = size - BUFFER_SIZE * math.floor(size / BUFFER_SIZE)
                print(buffi)
                
                while True:
                    data = sock.recv(BUFFER_SIZE)
                    if len(data) == buffi:
                        f.write(data)
                        break
                    f.write(data)
                f.close()
                
                print("File transfered!")
        elif 'stop' in command:
            break
        else:
            continue

    sock.close()
    return

while True:
    chooseRole = input()
    if chooseRole == "server":
        serverPart()
    elif chooseRole == 'client':
        clientPart()
    else:
        "Wrong role! Try again"