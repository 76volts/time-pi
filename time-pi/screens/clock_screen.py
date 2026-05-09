import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lcd")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rotary")))


from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

def format_time():
    now = datetime.now()
    return now.strftime("%I:%M:%S %p"), now.strftime("%a %d %b")

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    try:
        while True:
            current_time, current_date = format_time()
            lcd.write(current_time.center(20), line=0)
            lcd.write(current_date.center(20), line=1)
            lcd.write("Partly Cloudy", line=2)
            lcd.write("Temp: 24C", line=3)

            for _ in range(10):
                if rotary.read_button():
                    raise KeyboardInterrupt
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
