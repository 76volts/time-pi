import pigpio
import time

class RotaryEncoder:
    def __init__(self, clk_pin=17, dt_pin=18, sw_pin=27):
        self.CLK = clk_pin
        self.DT = dt_pin
        self.SW = sw_pin

        self.position = 0
        self.button_pressed = False
        self._last_rotation_time = 0
        self._last_button_time = 0

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Cannot connect to pigpio daemon")

        self.pi.set_mode(self.CLK, pigpio.INPUT)
        self.pi.set_mode(self.DT, pigpio.INPUT)
        self.pi.set_mode(self.SW, pigpio.INPUT)

        self.pi.set_pull_up_down(self.CLK, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.DT, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.SW, pigpio.PUD_UP)

        self.cb_clk = self.pi.callback(self.CLK, pigpio.EITHER_EDGE, self._rotation_callback)
        self.cb_dt = self.pi.callback(self.DT, pigpio.EITHER_EDGE, self._rotation_callback)
        self.cb_sw = self.pi.callback(self.SW, pigpio.FALLING_EDGE, self._button_callback)

        self.last_encoded = (self.pi.read(self.CLK) << 1) | self.pi.read(self.DT)

    def _rotation_callback(self, gpio, level, tick):
        now = time.monotonic()
        if now - self._last_rotation_time < 0.001:
            return
        self._last_rotation_time = now

        clk_val = self.pi.read(self.CLK)
        dt_val = self.pi.read(self.DT)
        encoded = (clk_val << 1) | dt_val
        combined = (self.last_encoded << 2) | encoded

        if combined in [0b0001, 0b0111, 0b1110, 0b1000]:
            self.position += 1
        elif combined in [0b0010, 0b0100, 0b1101, 0b1011]:
            self.position -= 1

        self.last_encoded = encoded

    def _button_callback(self, gpio, level, tick):
        now = time.monotonic()
        if now - self._last_button_time < 0.4:
            return
        if self.pi.read(self.SW) == 0:
            self._last_button_time = now
            self.button_pressed = True

    def read_position(self):
        return self.position

    def reset_position(self):
        self.position = 0

    def read_button(self):
        if self.button_pressed:
            self.button_pressed = False
            return True
        return False

    def cleanup(self):
        self.cb_clk.cancel()
        self.cb_dt.cancel()
        self.cb_sw.cancel()
        self.pi.stop()


if __name__ == "__main__":
    encoder = RotaryEncoder()
    print("Rotate the encoder or press the button. Press Ctrl+C to exit.")
    try:
        while True:
            pos = encoder.read_position()
            print(f"Position: {pos:4d}", end='\r')
            if encoder.read_button():
                print("\nButton pressed")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        encoder.cleanup()
