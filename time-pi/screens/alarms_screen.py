import time
import sys
import os
from datetime import datetime

sys.path.insert(0, "./lcd")
sys.path.insert(0, "./rotary")
sys.path.insert(0, "./buzzer")

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder
from buzzer.manager import Buzzer

CONFIG_PATH = os.path.expanduser("~/time-pi/config/alarms.conf")

def load_alarms():
    alarms = []
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    time_str = parts[0]
                    label = parts[1]
                    days = parts[2:9]
                    alarms.append((time_str, label, days))
    return alarms

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()
    buzzer = Buzzer()

    alarms = load_alarms()

    try:
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_day_index = now.weekday()

            for alarm_time, label, days in alarms:
                if alarm_time == current_time and len(days) > current_day_index and days[current_day_index] != 'X':
                    lcd.clear()
                    lcd.write("!!! ALARM !!!", line=0)
                    lcd.write(f"{alarm_time} {label}", line=1)
                    buzzer.buzz(1000, 0.3)
                    time.sleep(0.3)
                    if rotary.read_button():
                        buzzer.stop()
                        raise KeyboardInterrupt
                    break

            if rotary.read_button():
                raise KeyboardInterrupt

            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        rotary.cleanup()
        buzzer.stop()

if __name__ == "__main__":
    main()
