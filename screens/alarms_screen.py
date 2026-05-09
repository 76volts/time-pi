import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lcd")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rotary")))

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

CONFIG_PATH = os.path.expanduser("~/time-pi/config/alarms.conf")

# Track which alarms fired today
triggered_today = set()

def load_alarms():
    """Load alarms from config/alarms.conf."""
    alarms = []
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    time_str = parts[0]
                    label = parts[1]
                    days = parts[2:9]
                    alarms.append((time_str, label, days))
    return alarms

def format_alarm_line(time_str, label):
    """Format alarm as 'HH:MM Label' truncated to 20 chars."""
    line = f"{time_str}  {label}"
    return line[:20].ljust(20)

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    alarms = load_alarms()

    try:
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_second = now.second
            current_day_index = now.weekday()  # 0=Mon, 6=Sun
            
            # Clear triggered alarms at midnight
            if current_time == "00:00" and current_second == 0:
                triggered_today.clear()

            # Check if any alarm should fire
            alarm_firing = False
            firing_alarm_idx = -1

            for idx, (alarm_time, label, days) in enumerate(alarms):
                alarm_key = f"{alarm_time}_{current_day_index}"

                # Check if this alarm should trigger
                if (alarm_time == current_time and 
                    len(days) > current_day_index and 
                    days[current_day_index] != 'X' and
                    alarm_key not in triggered_today):
                    
                    alarm_firing = True
                    firing_alarm_idx = idx
                    triggered_today.add(alarm_key)
                    break

            if alarm_firing:
                # Display firing alarm
                alarm_time, label, _ = alarms[firing_alarm_idx]
                lcd.clear()
                lcd.write("!!! ALARM !!!".center(20), line=0)
                lcd.write(format_alarm_line(alarm_time, label), line=1)
                lcd.write("Press to dismiss".center(20), line=2)
                lcd.write("".ljust(20), line=3)

                # Wait for button press to dismiss
                while True:
                    if rotary.read_button():
                        break
                    time.sleep(0.1)

            else:
                # Display list of configured alarms
                lcd.clear()
                lcd.write("Alarms".ljust(20), line=0)

                if not alarms:
                    lcd.write("No alarms set".center(20), line=1)
                    lcd.write("".ljust(20), line=2)
                    lcd.write("".ljust(20), line=3)
                else:
                    # Show first 3 alarms
                    for i in range(min(3, len(alarms))):
                        alarm_time, label, _ = alarms[i]
                        lcd.write(format_alarm_line(alarm_time, label), line=i + 1)

                # Check for exit
                if rotary.read_button():
                    raise KeyboardInterrupt

            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
