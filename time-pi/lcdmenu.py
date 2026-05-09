import time
import sys
import subprocess

sys.path.insert(0, "./lcd")
sys.path.insert(0, "./rotary")

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

MENU_ITEMS = [
    ("Clock", "screens/clock_screen.py"),
    ("Alarms", "screens/alarms_screen.py"),
    ("Events", "screens/events_screen.py"),
    ("Weather", "screens/weather_screen.py"),
    ("Quotes", "screens/quotes_screen.py")
]

def render_menu(lcd, options, selected_index):
    lcd.clear()
    window_size = 4
    start_index = max(0, selected_index - (window_size - 1))
    end_index = start_index + window_size

    for i in range(start_index, min(end_index, len(options))):
        prefix = ">" if i == selected_index else "  "
        lcd.write(f"{prefix} {options[i][0]}", line=i - start_index)

def launch_screen(script_path):
    subprocess.run(["python3", script_path])

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    selected = 0
    last_position = rotary.read_position()
    accumulated = 0
    scroll_threshold = 2

    render_menu(lcd, MENU_ITEMS, selected)

    try:
        while True:
            pos = rotary.read_position()
            delta = pos - last_position

            if delta != 0:
                accumulated += delta
                last_position = pos

                if abs(accumulated) >= scroll_threshold:
                    step = 1 if accumulated > 0 else -1
                    selected = (selected + step) % len(MENU_ITEMS)
                    render_menu(lcd, MENU_ITEMS, selected)
                    accumulated = 0

            if rotary.read_button():
                lcd.clear()
                lcd.write("Launching:", line=0)
                lcd.write(MENU_ITEMS[selected][0], line=1)
                time.sleep(1)
                lcd.clear()
                launch_screen(MENU_ITEMS[selected][1])
                render_menu(lcd, MENU_ITEMS, selected)

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nExiting menu.")
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
