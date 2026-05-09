import RPi.GPIO as GPIO
import time

# Define pins
button_pins = [22, 23, 24, 5, 6, 12]

# Setup
GPIO.setmode(GPIO.BCM)  # Use GPIO numbering
for pin in button_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up: pressed = LOW

print("Ready. Press any button (CTRL+C to exit).")

try:
    while True:
        for pin in button_pins:
            if GPIO.input(pin) == GPIO.LOW:
                print(f"Button on GPIO{pin} pressed!")
        time.sleep(0.1)  # debounce
except KeyboardInterrupt:
    print("Exiting.")

finally:
    GPIO.cleanup()
