import math
import time
import RPi.GPIO as GPIO
import threading
# Number of cells of the history array.
HISTORY_LENGTH = 200
# Duration of each history array cell (seconds).
HISTORY_UNIT = 6
# Process period for the statistics (milliseconds).
PROCESS_PERIOD = 160
MAX_CPM_TIME = HISTORY_LENGTH * HISTORY_UNIT * 1000
# Magic calibration number from the Arduino lib.
K_ALPHA = 53.032

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
        return dict(
            #duration=round(self.duration / 1000.0, 2),
            cpm=round(cpm, 2)
            #uSvh=round(cpm / K_ALPHA, 3),
            #uSvhError=round(math.sqrt(self.count) / minutes / K_ALPHA, 3)
            #if minutes > 0
            #else 0,
        )
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
''' if __name__ == "__main__":
    with RadiationWatch(24,23) as radiationWatch:
        while 1:
            print(radiationWatch.status())
            time.sleep(1)'''
