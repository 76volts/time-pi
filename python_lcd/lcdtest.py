from i2c_lcd import I2cLcd
import smbus2
import time

# I2C device address (double-check using `i2cdetect -y 1`)
I2C_ADDR = 0x27
I2C_BUS = 1  # Raspberry Pi typically uses bus 1

# Initialize LCD: 20 characters, 4 lines
lcd = I2cLcd(1, I2C_ADDR, 4, 20)

lcd.backlight_on()
lcd.clear()
lcd.putstr("Lisa is a silly goose.")
time.sleep(10)
lcd.clear()
lcd.backlight_off()

