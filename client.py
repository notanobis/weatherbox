import socket
import ipaddress
from all1 import*
import time
from datetime import datetime
import pickle
import sys
import pandas as pd
#from humidity import take_data
from timeit import default_timer as timer
import random
import matplotlib.pyplot as plt
import threading
import ctypes

HEADER = 64
PORT = 5005
FORMAT = 'utf-8'

DISCONNECT_MESSAGE = 'DISCONNECT'
SERVER = ipaddress.ip_address("192.168.1.19")
ADDR = (str(SERVER),PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect(ADDR) # inerver -> bind

def send(msg):
    #message = msg.encode(FORMAT) #from string to bytes in order to send the msg
    #msg_length = len(message)
    #send_length = str(msg_length).encode(FORMAT)
    #i have to make sure that it is going to be 64
    # send_length += b' ' * (HEADER-len(send_length))
    #client.send(send_length)
    client.send(msg)

from multiprocessing.pool import ThreadPool

pool = ThreadPool()
times1=[]
times2= []
times3 =[]
times4 =[]

if __name__ == "__main__":
    # Create the RadiationWatch object, specifying the used GPIO pins ...
   #
    with RadiationWatch(24, 23) as radiationWatch:
        

        for _ in range(100):
            # ... and simply print readings each 1 seconds.
            
            result1 = pool.apply_async(take_hum)
            result1['TIME'] = datetime.now()
            times1.append(result1['TIME'])
            send(pickle.dumps(result1.get()))
            
            result2 = pool.apply_async(take_temp)
            result2['TIME'] = datetime.now()
            times2.append(result2['TIME'])
            send(pickle.dumps(result2.get()))
            
            result3 = pool.apply_async(temps)
            result3['TIME'] = datetime.now()
            times3.append(result3['TIME'])
            send(pickle.dumps(result3.get()))
            
            result4 = pool.apply_async(radiationWatch.status)
            result4['TIME'] = datetime.now()
            times4.append(result4['TIME'])
            send(pickle.dumps(result4.get()))
#             
    plt.plot(times1, label = "hum")
    plt.plot(times2, label = "temp")
    plt.plot(times3, label = "pt100")
    plt.plot(times4, label = "radiation")
    plt.legend()
    plt.show()            
             
    
