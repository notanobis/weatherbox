###Lybraries used:
#adafruit-circuitpython-ads1x15 | adafruit-circuitpython-lis3dh | sympy

import board
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from sympy import Symbol
from sympy.solvers import solve


i2c=busio.I2C(board.SCL,board.SDA)
ads=ADS.ADS1115(i2c)
chan0=AnalogIn(ads,ADS.P0)
chan1=AnalogIn(ads,ADS.P1)

while True:

    #vi=voltage pt100 / vcc=voltage source(3.3V) / i=current / R= rtc resistance
    vi=chan0.voltage
    vcc=chan1.voltage
    R=3300/(vcc/vi-1)
    i=vi/R

    #constants of pt100 
    a=3.9083*10**(-3)
    b=-5.775*10**(-7)
    c=-4.183*10**(-12)

    #Finding temperature through resistance (rtc curve)
    x=Symbol("x")
    if R>100:
       T=solve(R-100*(1+a*x+b*x**2),x)
    else:
        T=solve(R-100*(1+a*x+b*x**2+c*(x-100)*x**3),x)

    #keeping only the value within the reasonable range of temperatures
    for z in range(0,len(T)):
        if T[z]>=-200 and T[z]<=300:
            temp=T[z]
            print(temp)
        z=z+1
    time.sleep(0.5)