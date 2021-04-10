import socket
import threading


HEADER = 64 #in the first msg to the server from client is going to tell us the length of the msf tha is going to come next

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
#ADDR = ('', PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = 'DISCONNECT' #close the connection and disconnect client from server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('192.168.1.9', 5050))

def handle_client(conn, addr): #handle individual connection
    print(f"[NEW CONNECTION] {addr} connected.\n")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT) #the received msg -> wait until smthg is send from the socket
        #inside the recv() we have how many bytes we receive from the client so i create a header
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}") # address of client and the msg
    conn.close()

def start():        #handle new connection
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}" )
    while True:
        conn, addr = server.accept() #wait for a new connection to the server -> conn : socket object info about connection
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}") #print active connections

print("[STARTING] server is starting...")

start()

