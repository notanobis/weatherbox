import socket
import ipaddress
from humidity import take_data
from radiation3 import RadiationWatch
import time

#from humidity import take_data

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'

DISCONNECT_MESSAGE = 'DISCONNECT'
SERVER = ipaddress.ip_address("192.168.1.4")
ADDR = (str(SERVER),PORT)
print(ADDR)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR) # in server -> bind

def send(msg):
    message = msg.encode(FORMAT) #from string to bytes in order to send the msg
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    #i have to make sure that it is going to be 64
    send_length += b' ' * (HEADER-len(send_length))
    client.send(send_length)
    client.send(message)
#send(str(take_data()))
#send(str(radiationWatch.status()))
     
#send(DISCONNECT_MESSAGE)


if __name__ == "__main__":
    # Create the RadiationWatch object, specifying the used GPIO pins ...
    with RadiationWatch(24, 23) as radiationWatch:
        while 1:
            # ... and simply print readings each 1 seconds.
            send(str(radiationWatch.status()))
            send(str(take_data()))
            time.sleep(1)
