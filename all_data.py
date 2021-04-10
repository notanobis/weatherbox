from humidity import take_data
from radiation3 import RadiationWatch
import time

if __name__ == "__main__":
    # Create the RadiationWatch object, specifying the used GPIO pins ...
    with RadiationWatch(24, 23) as radiationWatch:
        while 1:
            # ... and simply print readings each 1 seconds.
            print(radiationWatch.status())
            take_data()
            time.sleep(0.5)


