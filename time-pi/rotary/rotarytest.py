# rotary/test_rotary.py

import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rotary.manager import RotaryEncoder

encoder = RotaryEncoder()

try:
    print("Rotate the knob or press the button (CTRL+C to quit)")
    while True:
        val = encoder.read_rotation()
        print(f"Value: {val}", end='\r')
        if encoder.is_pressed():
            print("\nButton Pressed!")
            time.sleep(0.3)  # debounce
        time.sleep(0.01)
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    encoder.cleanup()
