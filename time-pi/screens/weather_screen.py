import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lcd")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rotary")))

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    lcd.clear()
    lcd.write("Weather Report", line=0)
    lcd.write("(Placeholder)", line=1)

    try:
        while True:
            if rotary.read_button():
                break
            time.sleep(0.1)
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
