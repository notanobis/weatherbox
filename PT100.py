###Lybraries used:
#adafruit-circuitpython-ads1x15 | adafruit-circuitpython-lis3dh | sympy
def temps():
    import board
    import time
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    from sympy import Symbol
    from sympy.solvers import solve


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

    #constants of pt100 
    a=3.9083*10**(-3)
    b=-5.775*10**(-7)
    c=-4.183*10**(-12)


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

    for z in range(0,len(T2)):
        if T2[z]>=-200 and T2[z]<=300:
            T2[z]=float("{:.2f}".format(T2[z]))
            temp.append(T2[z])

    for z in range(0,len(T3)):
        if T3[z]>=-200 and T3[z]<=300:
            T3[z]=float("{:.2f}".format(T3[z]))
            temp.append(T3[z])

    for z in range(0,len(T4)):
        if T4[z]>=-200 and T4[z]<=300:
            T4[z]=float("{:.2f}".format(T4[z]))
            temp.append(T4[z])

    return temp
