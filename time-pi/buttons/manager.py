import RPi.GPIO as GPIO
import time
import threading

class ButtonManager:
    def __init__(self, button_pins=None):
        if button_pins is None:
            # Default to your 8 button GPIOs
            button_pins = [22, 23, 5, 24, 6, 25, 13, 12]
        self.button_pins = button_pins
        self.callbacks = {}
        self.running = False
        self.lock = threading.Lock()

        GPIO.setmode(GPIO.BCM)
        for pin in self.button_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self._handle_press, bouncetime=200)

    def _handle_press(self, pin):
        with self.lock:
            if pin in self.callbacks:
                self.callbacks[pin]()

    def register_callback(self, pin, callback):
        if pin in self.button_pins:
            self.callbacks[pin] = callback
        else:
            raise ValueError(f"Pin {pin} is not a registered button.")

    def cleanup(self):
        GPIO.cleanup()

# Basic test block (can be deleted if importing into main)
if __name__ == "__main__":
    def test_callback(pin):
        print(f"Button on GPIO{pin} pressed.")

    manager = ButtonManager()
    for pin in manager.button_pins:
        manager.register_callback(pin, lambda p=pin: test_callback(p))

    print("Press buttons (Ctrl+C to exit)...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting.")
        manager.cleanup()

