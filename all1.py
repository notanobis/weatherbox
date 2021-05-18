###Lybraries used:
#adafruit-circuitpython-ads1x15 | adafruit-circuitpython-lis3dh | sympy
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from sympy import Symbol
from sympy.solvers import solve
import Adafruit_DHT
import os
import math
import time
import RPi.GPIO as GPIO
import threading


#constants of pt100 
a=3.9083*10**(-3)
b=-5.775*10**(-7)
c=-4.183*10**(-12)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
# Number of cells of the history array.
HISTORY_LENGTH = 200
# Duration of each history array cell (seconds).
HISTORY_UNIT = 6
# Process period for the statistics (milliseconds).
PROCESS_PERIOD = 160
MAX_CPM_TIME = HISTORY_LENGTH * HISTORY_UNIT * 1000
# Magic calibration number from the Arduino lib.
K_ALPHA = 53.032

i2c=busio.I2C(board.SCL,board.SDA)
ads1=ADS.ADS1115(i2c)
ads2=ADS.ADS1115(i2c,address=0x49)
ads3=ADS.ADS1115(i2c,address=0x4A)
ads4=ADS.ADS1115(i2c,address=0x4B)
chan01=AnalogIn(ads1,ADS.P0)
chan11=AnalogIn(ads1,ADS.P1)
chan02=AnalogIn(ads2,ADS.P0)
chan12=AnalogIn(ads2,ADS.P1)
chan03=AnalogIn(ads3,ADS.P0)
chan13=AnalogIn(ads3,ADS.P1)
chan04=AnalogIn(ads4,ADS.P0)
chan14=AnalogIn(ads4,ADS.P1)

def temps(name, position):
    #vi=voltage pt100 / vcc=voltage source(3.3V) / R= rtc resistance
    vi1=chan01.voltage
    vcc1=chan11.voltage
    vi2=chan02.voltage
    vcc2=chan12.voltage
    vi3=chan03.voltage
    vcc3=chan13.voltage
    vi4=chan04.voltage
    vcc4=chan14.voltage

    R1=3300/(vcc1/vi1-1)
    R2=3300/(vcc2/vi2-1)
    R3=3300/(vcc3/vi3-1)
    R4=3300/(vcc4/vi4-1)


    #Finding temperature through resistance (rtc curve)
    x=Symbol("x")
    

    if R1>100:
        T1=solve(R1-100*(1+a*x+b*x**2),x)
    else:
        T1=solve(R1-100*(1+a*x+b*x**2+c*(x-100)*x**3),x)

    if R2>100:
        T2=solve(R2-100*(1+a*x+b*x**2),x)
    else:
        T2=solve(R2-100*(1+a*x+b*x**2+c*(x-100)*x**3),x)

    if R3>100:
        T3=solve(R3-100*(1+a*x+b*x**2),x)
    else:
        T3=solve(R3-100*(1+a*x+b*x**2+c*(x-100)*x**3),x)

    if R4>100:
        T4=solve(R4-100*(1+a*x+b*x**2),x)
    else:
        T4=solve(R4-100*(1+a*x+b*x**2+c*(x-100)*x**3),x)

    #keeping only the value within the reasonable range of temperatures
    temp=[]
    for z in range(0,len(T1)):
        if T1[z]>=-200 and T1[z]<=300:
            T1[z]=float("{:.2f}".format(T1[z]))
            temp.append(T1[z])
        z=z+1

    for z in range(0,len(T2)):
        if T2[z]>=-200 and T2[z]<=300:
            T2[z]=float("{:.2f}".format(T2[z]))
            temp.append(T2[z])
        z=z+1 

    for z in range(0,len(T3)):
        if T3[z]>=-200 and T3[z]<=300:
            T3[z]=float("{:.2f}".format(T3[z]))
            temp.append(T3[z])
        z=z+1

    for z in range(0,len(T4)):
        if T4[z]>=-200 and T4[z]<=300:
            T4[z]=float("{:.2f}".format(T4[z]))
            temp.append(T4[z])
        z=z+1
    dict = {"name": "{}_PT100[*C]".format(name), "value": temp[position]}
    return dict

def take_hum():
    humidity, temperature =  Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    dict1 = {"name": "Humidity[%]", "value":float("{:.2f}".format(humidity))}
    return dict1

def take_temp():
        humidity, temperature =  Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        dict1 = {"name": "Temperature[*C]", "value": float("{:.2f}".format(temperature))}
        return dict1
    
def millis():
    """Return current time in milliseconds.
    """
    return int(round(time.time() * 1000))

class RadiationWatch:
    def __init__(self,radiation_pin, noise_pin, numbering = GPIO.BCM):
        GPIO.setmode(numbering)
        self.radiation_pin = radiation_pin
        self.noise_pin = noise_pin
        self.mutex = threading.Lock()
    def status(self):
        """Return current readings, as a dictionary with:
            duration -- the duration of the measurements, in seconds;
            cpm -- the radiation count by minute;
            uSvh -- the radiation dose, expressed in microSieverts per hour (uSv/h);
            uSvhError -- the incertitude for the radiation dose."""
        minutes = min(self.duration, MAX_CPM_TIME) / 1000 / 60.0
        cpm = self.count / minutes if minutes > 0 else 0
        dict1 = {"name": "Radiation[cpm]", "value": cpm}
        return dict1
        
    def __enter__(self):
        return self.setup()
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def setup(self):
        """Initialize the driver by setting up GPIO interrupts
        and periodic statistics processing. """
        # Initialize the statistics variables.
        self.radiation_count = 0
        self.noise_count = 0
        self.count = 0
        self.count_history = [0] * HISTORY_LENGTH
        self.history_index = 0
        self.previous_time = millis()
        self.previous_history_time = millis()
        self.duration = 0
        GPIO.setup(self.radiation_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.noise_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self._enable_timer()
        return self
    def close(self):
        """Properly close the resources associated with the driver
        (GPIOs and so on)."""
        # Clean up only used channels.
        GPIO.cleanup([self.radiation_pin, self.noise_pin])
        with self.mutex:
            self.timer.cancel()
            
    def _enable_timer(self):
        self.timer = threading.Timer(PROCESS_PERIOD / 1000.0, self._process_statistics)
        self.timer.start()
    def _process_statistics(self):
        with self.mutex:
            current_time = millis()
            current_radiation_count = self.radiation_count
            current_noise_count = self.noise_count
            self.radiation_count = 0
            self.noise_count = 0
        if current_noise_count == 0:
            # Store count log.
            self.count_history[self.history_index] += current_radiation_count
            # Add number of counts.
            self.count += current_radiation_count
            # Add ellapsed time to history duration.
            self.duration += abs(current_time - self.previous_time)
        # Shift an array for counting log for each HISTORY_UNIT seconds.
        if current_time - self.previous_history_time >= HISTORY_UNIT * 1000:
            self.previous_history_time += HISTORY_UNIT * 1000
            self.history_index = (self.history_index + 1) % HISTORY_LENGTH
            self.count -= self.count_history[self.history_index]
            self.count_history[self.history_index] = 0
        # Save time of current process period.
        self.previous_time = millis()
        # Enable the timer again.
        if self.timer:
            self._enable_timer()
