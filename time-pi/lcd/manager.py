import smbus2
import time
import atexit

from lcd.lcd_api import LcdApi
from lcd.i2c_lcd import I2cLcd


class LCDManager:
    I2C_ADDR = 0x27
    LCD_WIDTH = 20
    LCD_HEIGHT = 4
    I2C_BUS = 1

    def __init__(self):
        self.lcd = I2cLcd(self.I2C_BUS, self.I2C_ADDR, self.LCD_HEIGHT, self.LCD_WIDTH)
        atexit.register(self.cleanup)
        self.clear()

    def write(self, text: str, line: int = 0, align: str = "left"):
        if not 0 <= line < self.LCD_HEIGHT:
            raise ValueError("Line must be between 0 and 3")

        text = text.strip()
        if align == "center":
            text = text.center(self.LCD_WIDTH)
        elif align == "right":
            text = text.rjust(self.LCD_WIDTH)
        else:
            text = text.ljust(self.LCD_WIDTH)

        self.lcd.move_to(0, line)
        self.lcd.putstr(text[:self.LCD_WIDTH])

    def clear(self):
        self.lcd.clear()

    def backlight(self, on: bool):
        if on:
            self.lcd.backlight_on()
        else:
            self.lcd.backlight_off()

    def cleanup(self):
        try:
            self.clear()
            self.backlight(False)
        except Exception:
            pass  # Prevent crashes on exit


if __name__ == "__main__":
    lcd = LCDManager()
    lcd.write("Funny Valentine", line=0, align="center")
    lcd.write("Protocol Online", line=1, align="center")
    time.sleep(3)
    lcd.clear()
