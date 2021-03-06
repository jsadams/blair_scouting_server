import socket
from threading import Thread

import printing
from datactl import addtoqueue
from system import gethostMAC

PORT = 1
BACKLOG = 1
SIZE = 1024

MAC_DICT = {'78:E1:03:A4:F7:70': 'Poseidon',
            '00:FC:8B:3B:42:46': 'Demeter',
            '00:FC:8B:39:C1:09': 'Hestia',
            '78:E1:03:A1:E2:F2': 'Hades',
            '78:E1:03:A3:18:78': 'Hera',
            '???': '???',
            '00:FC:8B:3F:28:28': 'Backup 1',
            '00:FC:8B:3F:E4:EF': 'Zeus',  # Secretly Backup 2
            '44:65:0D:E0:D6:3A': 'Strategy Tablet'}


def init():
    global server_sock, clients

    host_mac = gethostMAC()

    # Setup server socket
    server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server_sock.bind((host_mac, PORT))
    server_sock.listen(BACKLOG)
    server_sock.settimeout(None)

    clients = []


# Read loop to continually read data from a client
def read(sock, info):
    try:
        # Receive data
        data = sock.recv(SIZE)

        str_data = data.decode()

        addtoqueue(str_data, MAC_DICT.get(info, info))

        # Wait for the next match
        read(sock, info)
    except ConnectionResetError:
        printing.printf('Disconnected from', MAC_DICT.get(info, info), style=printing.DISCONNECTED)
        sock.close()
        clients.remove((sock, info))
    except TimeoutError:
        printing.printf('Timeout on ' + MAC_DICT.get(info, info) + ', restarting sock.recv (this is probably fine, '
                                                                   'though it shouldn\'t be happening)')
        read(sock, info)


# Waits for a device to try to connect, then starts a thread to read that device, and stays open for connections
def connect():
    # Wait for connection
    client_sock, client_info = server_sock.accept()
    # Connect to device
    printing.printf('Accepted connection from', MAC_DICT.get(client_info[0], client_info[0]), style=printing.CONNECTED)
    clients.append((client_sock, client_info[0]))

    # Start reading it
    Thread(target=lambda: read(client_sock, client_info[0])).start()

    # Stay open for connections
    connect()


# Closes all connections and the server
def close():
    for sock in clients:
        sock[0].close()
        printing.printf('Closed connection with', MAC_DICT.get(sock[1], sock[1]), style=printing.STATUS)
    clients.clear()
    server_sock.close()
    printing.printf('Closed server', style=printing.STATUS)
