import socket
import ipaddress
from all1 import*
import time
from datetime import datetime
import pickle
import sys
import pandas as pd
from timeit import default_timer as timer
import random
import matplotlib.pyplot as plt
import threading
import ctypes
import json

PORT = 5005
SERVER = ipaddress.ip_address("192.168.1.3")
ADDR = (str(SERVER),PORT)

#creating the socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect(ADDR) 

def send(msg):
        client.send(pickle.dumps(msg))

def send_radiation():
    with RadiationWatch(24, 23) as radiationWatch:
        while 1:
            radiation = radiationWatch.status()
            radiation['date'] = datetime.now()
            send(radiation)
            time.sleep(1)

def send_temp_dht22():
    while 1:
        temperature = take_temp()
        temperature['date'] = datetime.now()
        send(temperature)
        time.sleep(1)


def send_hum():
    while 1:
        humidity = take_hum()
        humidity['date'] = datetime.now()
        send(humidity)
        time.sleep(1)

def send_temp_pt100():
    while 1:
        pt100_te = temps("East", 0)
        pt100_te['date'] = datetime.now()
        send(pt100_te)
        pt100_ts = temps("South", 1)
        pt100_ts['date'] = datetime.now()
        send(pt100_ts)
        pt100_tn = temps("North", 2)
        pt100_tn['date'] = datetime.now()
        send(pt100_tn)
        pt100_tw = temps("West", 3)
        pt100_tw['date'] = datetime.now()
        send(pt100_tw)
      
def send_temp_pt100_South():
    while 1:
        pt100_t = temps("South", 2)
        pt100_t['date'] = datetime.now()
        send(pt100_t)

def send_temp_pt100_North():
    while 1:
        pt100_t = temps("North", 1)
        pt100_t['date'] = datetime.now()
        send(pt100_t)

def send_temp_pt100_West():
    while 1:
        pt100_t = temps("West", 3)
        pt100_t['date'] = datetime.now()
        send(pt100_t)

rs = threading.Thread(target = send_radiation)
hs = threading.Thread(target = send_hum)
ts_dht22 = threading.Thread(target = send_temp_dht22)
ts_pt100 = threading.Thread(target = send_temp_pt100)


ts_pt100.start()
rs.start()
hs.start()
ts_dht22.start()

ts_pt100.join()
rs.join()
hs.join()
ts_dht22.join()