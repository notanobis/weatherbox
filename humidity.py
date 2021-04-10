import Adafruit_DHT
import os
import time
#import humidity.py as  

DHT_SENSOR = Adafruit_DHT.DHT22

DHT_PIN = 4

def take_data():
    humidity, temperature =  Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    d = {'date': time.strftime('%m/%d/%y'),
         'time' : time.strftime('%H:%M'),
         'tem':temperature,
         'hum' : humidity}
    return d    

