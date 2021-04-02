import Adafruit_DHT
import os
import time
#import humidity.py as  

DHT_SENSOR = Adafruit_DHT.DHT22

DHT_PIN = 4

while True:
    humidity, temperature =  Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        print('{0},{1},{2:0.1f}*C,{3:0.1f}%\r\n'.format(time.strftime('%m/%d/%y'),time.strftime('%H:%M'),temperature, humidity))

    else:
        print("Failed to retrieve data from humidity sensor")
    time.sleep(1)

