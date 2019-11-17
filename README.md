# BluetoothServer
Part of 1st laboratory "Mobile technologies &amp; means of communication" in Peter the Great St.Petersburg Polytechnic University.

## Built With 
* PyBluez - [Bluetooth Python extension module](https://github.com/pybluez/pybluez)
* PyAutoGUI - [A cross-platform GUI automation Python module for human beings](https://github.com/asweigart/pyautogui)

## Usage
1. Firstly you need to pair devices, that will be sharing.
2. Server needs to be run first 
3. Client connecting to server via MAC-address
4. Write commands on client side

## Commands
* command screenshot – client recieve screenshot of server device
* command file *file_path* – client recieve file from server by *file_path* path
* command receive screenshot – client send screenshot of device to server
* command receive *file_path* – client send file to server from *file_path* path
* stop – stop server and client

## Authors
* **Andrey Kim** - [kimoofey](https://github.com/kimoofey)
