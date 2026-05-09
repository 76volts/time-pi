from lcd.manager import LCDManager
from rtc.manager import RTCManager
import time
import signal
import sys


def graceful_exit(lcd):
    lcd.clear()
    lcd.backlight(False)
    sys.exit(0)


def main():
    lcd = LCDManager()
    rtc = RTCManager()

    signal.signal(signal.SIGINT, lambda sig, frame: graceful_exit(lcd))

    while True:
        now = rtc.read_datetime()
        lcd.write("System Clock", line=0, align="center")
        lcd.write(now.strftime("%Y-%m-%d"), line=1, align="center")
        lcd.write(now.strftime("%H:%M:%S"), line=2, align="center")
        time.sleep(1)


if __name__ == "__main__":
    main()
