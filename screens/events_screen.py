import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lcd")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rotary")))

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

CONFIG_PATH = os.path.expanduser("~/time-pi/config/events.conf")

def load_events():
    """
    Load events from config/events.conf.
    Format: YYYY-MM-DD  Label (space-separated)
    Returns: list of (date_obj, label_str) tuples, sorted by date
    """
    events = []

    if not os.path.exists(CONFIG_PATH):
        return events

    try:
        with open(CONFIG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split(None, 1)  # Split on first whitespace
                if len(parts) < 2:
                    continue

                date_str = parts[0]
                label = parts[1]

                try:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    events.append((event_date, label))
                except ValueError:
                    # Skip malformed date
                    continue

    except IOError:
        pass

    # Sort by date and filter out past events
    today = datetime.now().date()
    future_events = [(d, l) for d, l in events if d >= today]
    future_events.sort(key=lambda x: x[0])

    return future_events

def days_until(event_date):
    """Return number of days from today to event_date."""
    today = datetime.now().date()
    delta = event_date - today
    return delta.days

def format_event_line(event_date, label):
    """
    Format an event as "Label  Nd" where N is days remaining.
    Max width: 20 chars.
    """
    days = days_until(event_date)
    if days == 0:
        days_str = "Today"
    elif days == 1:
        days_str = "1d"
    else:
        days_str = f"{days}d"

    # Truncate label to fit with days_str
    max_label_len = 20 - len(days_str) - 2  # -2 for spacing
    truncated_label = label[:max_label_len]

    line = f"{truncated_label:<{max_label_len}}  {days_str}"
    return line[:20].ljust(20)  # Ensure exactly 20 chars

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    try:
        while True:
            events = load_events()

            if not events:
                # No events file or all events are in the past
                lcd.clear()
                lcd.write("Upcoming Events".center(20), line=0)
                lcd.write("No events found".center(20), line=1)
                lcd.write("Add to".center(20), line=2)
                lcd.write("events.conf".center(20), line=3)

                # Wait for button press
                while True:
                    if rotary.read_button():
                        raise KeyboardInterrupt
                    time.sleep(0.1)

            # Normal operation: display events
            scroll_index = 0
            last_button_time = 0

            while True:
                # Display 3 events starting from scroll_index
                lcd.clear()
                lcd.write("Upcoming Events".ljust(20), line=0)

                for i in range(3):
                    event_idx = scroll_index + i
                    if event_idx < len(events):
                        event_date, label = events[event_idx]
                        line_text = format_event_line(event_date, label)
                        lcd.write(line_text, line=i + 1)
                    else:
                        lcd.write("".ljust(20), line=i + 1)

                # Check for button press (exit)
                if rotary.read_button():
                    raise KeyboardInterrupt

                # Check for rotation (scroll through events if >3 exist)
                pos = rotary.read_position()
                if pos > 0:
                    if scroll_index + 3 < len(events):
                        scroll_index += 1
                        rotary.reset_position()
                elif pos < 0:
                    if scroll_index > 0:
                        scroll_index -= 1
                        rotary.reset_position()

                time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
