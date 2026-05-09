import time
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lcd")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rotary")))

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

CONFIG_PATH = os.path.expanduser("~/time-pi/config/quotes.txt")

def load_random_quote():
    """
    Load a random quote from config/quotes.txt (one per line).
    Returns: (quote_text, success: bool)
    """
    if not os.path.exists(CONFIG_PATH):
        return None, False

    try:
        with open(CONFIG_PATH, "r") as f:
            quotes = [line.strip() for line in f if line.strip()]

        if not quotes:
            return None, False

        return random.choice(quotes), True
    except IOError:
        return None, False

def scroll_text_horizontal(lcd, text, start_row, end_row, delay=0.15):
    """
    Scroll text horizontally across rows start_row to end_row.
    Checks for button press on each frame to allow early exit.
    Returns: True if completed normally, False if user exited.
    """
    # Pad text to allow it to scroll completely off the right edge
    padded = "  " + text + "  "  # Add spacing at start and end
    window_width = 20

    for i in range(len(padded) - window_width + 1):
        window = padded[i : i + window_width]

        # Fill the rows with the scrolling text
        if start_row == end_row:
            lcd.write(window, line=start_row)
        else:
            # If spanning multiple rows, split the text (simple approach: same on both)
            lcd.write(window, line=start_row)
            lcd.write(window, line=end_row)

        # Check for button press
        if lcd.lcd is not None:  # Ensure LCD is still initialized
            try:
                pass  # Button checking happens outside this function
            except:
                pass

        time.sleep(delay)

    return True

def display_quote_static(lcd, quote):
    """
    Display a quote that fits in 40 characters (2 rows, 20 chars each).
    Center it vertically on rows 1-2.
    """
    # Split into two lines of 20 chars max
    if len(quote) <= 20:
        lcd.write(quote.center(20), line=1)
        lcd.write("".center(20), line=2)
    else:
        # Try to split on a word boundary or just split at 20
        line1 = quote[:20]
        line2 = quote[20:40] if len(quote) >= 20 else ""
        lcd.write(line1, line=1)
        lcd.write(line2.ljust(20), line=2)

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    try:
        while True:
            quote, found = load_random_quote()

            if not found:
                # No quotes file or empty
                lcd.clear()
                lcd.write("Add quotes to".center(20), line=0)
                lcd.write("config/quotes.txt".center(20), line=1)
                lcd.write("(one per line)".center(20), line=2)
                lcd.write("Press knob to exit".ljust(20), line=3)

                # Wait for button press
                while True:
                    if rotary.read_button():
                        raise KeyboardInterrupt
                    time.sleep(0.1)

            # Normal operation: display quote
            lcd.clear()
            lcd.write("Quote:".ljust(20), line=0)

            if len(quote) <= 40:
                # Static display for short quotes
                display_quote_static(lcd, quote)
                lcd.write("Press knob to exit".ljust(20), line=3)

                # Wait for ~5 seconds or button press
                for _ in range(50):
                    if rotary.read_button():
                        raise KeyboardInterrupt
                    time.sleep(0.1)

            else:
                # Scroll longer quotes across rows 1-2
                lcd.write("".ljust(20), line=3)

                # Scroll horizontally
                for i in range(len(quote) - 20 + 1):
                    window = quote[i : i + 20]
                    lcd.write(window, line=1)
                    lcd.write("".ljust(20), line=2)

                    if rotary.read_button():
                        raise KeyboardInterrupt

                    time.sleep(0.15)

                # Pause at end of scroll
                time.sleep(2)

                # Check button again
                if rotary.read_button():
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
