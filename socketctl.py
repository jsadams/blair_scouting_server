import socket
from threading import Thread
from queue import Queue

from dataconstants import GETDATA_TRIGGER
from getdata import get_data

# This should be the MAC address of your Bluetooth adapter
# Carter's desktop (essuomelpmap)
# HOST_MAC = '00:1A:7D:DA:71:13'

# Nate's laptop (DESKTOP-9HL0MM7)
# HOST_MAC = 'E4:F8:9C:BC:93:0E'

# Carter's laptop (gallium)
HOST_MAC = 'A4:C4:94:4F:6F:63'

PORT = 1
BACKLOG = 1
SIZE = 1024

MAC_DICT = {'78:E1:03:A4:F7:70': 'Poseidon', '44:65:0D:E0:D6:3A': 'Strategy Tablet'}

# Setup server socket
server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server_sock.bind((HOST_MAC, PORT))
server_sock.listen(BACKLOG)

clients = []


# Read loop to continually read data from a client
def read(sock, info):
    try:
        # Receive data
        data = sock.recv(SIZE)
        str_data = data.decode()
        if str_data[:len(GETDATA_TRIGGER)] == GETDATA_TRIGGER:
            # If it is a strategy request, return the data
            print('Data request ' + str_data[len(GETDATA_TRIGGER)+1:])
            # sock.send(bytes(get_data(data.split(':')[1]), 'UTF-8'))
            print(get_data(str_data.split()[1:]))
        else:
            # Add it to the data file
            to_add.put((info, str_data))
            # Print summary to server
            match = str_data[1].split(',')
            print('Data from ' + match[0] + ' on ' + MAC_DICT.get(match[0], match[0]) + ' for team ' +
                  match[2] + ' in match ' + match[1])
        # Wait for the next match
        read(sock, info)
    except ConnectionResetError:
        print('Disconnected from', info)
        sock.close()
        clients.remove((sock, info))


# Waits for a device to try to connect, then starts a thread to read that device, and stays open for connections
def connect():
    # Wait for connection
    client_sock, client_info = server_sock.accept()
    # Connect to device
    print('Accepted connection from', MAC_DICT.get(client_info[0], client_info[0]))
    clients.append((client_sock, client_info[0]))

    # Start reading it
    Thread(target=lambda: read(client_sock, client_info[0])).start()

    # Stay open for connections
    connect()


def close():
    for sock in clients:
        sock[0].close()
        print('Closed connection with', sock[1])
    server_sock.close()
    print('Closed server')