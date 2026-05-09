import time
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lcd")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rotary")))

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

# ============================================================================
# CGRAM Custom Character Definitions (6 building blocks)
# Each row is a 5-bit bitmask: 0b11111 = all 5 pixels on, 0b10001 = left & right edges
# ============================================================================

CGRAM_CHARS = {
    0: [  # Top-left corner (square top-left)
        0b11111,
        0b11111,
        0b11000,
        0b11000,
        0b11000,
        0b11000,
        0b11000,
        0b11000,
    ],
    1: [  # Top bar (horizontal line)
        0b11111,
        0b11111,
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b00000,
    ],
    2: [  # Top-right corner
        0b11111,
        0b11111,
        0b00011,
        0b00011,
        0b00011,
        0b00011,
        0b00011,
        0b00011,
    ],
    3: [  # Bottom-left corner
        0b11000,
        0b11000,
        0b11000,
        0b11000,
        0b11000,
        0b11111,
        0b11111,
        0b11111,
    ],
    4: [  # Bottom bar
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b11111,
        0b11111,
        0b11111,
    ],
    5: [  # Bottom-right corner
        0b00011,
        0b00011,
        0b00011,
        0b00011,
        0b00011,
        0b11111,
        0b11111,
        0b11111,
    ],
}

# ============================================================================
# Digit Rendering Map: which CGRAM chars to use for each digit (and spaces)
# Format: [top_left, top_mid, top_right, bottom_left, bottom_mid, bottom_right]
# 255 = full block (builtin), 32 = space, 0-5 = custom CGRAM slots
# ============================================================================

DIGIT_MAP = {
    # Format per digit: top row [left, mid, right], bottom row [left, mid, right]
    '0': ([0, 1, 2], [3, 4, 5]),
    '1': ([32, 32, 2], [32, 32, 5]),
    '2': ([0, 1, 2], [3, 4, 4]),
    '3': ([0, 1, 2], [32, 4, 5]),
    '4': ([0, 32, 2], [32, 32, 5]),
    '5': ([0, 1, 1], [3, 4, 5]),
    '6': ([0, 1, 1], [3, 4, 5]),
    '7': ([0, 1, 2], [32, 32, 5]),
    '8': ([0, 1, 2], [3, 4, 5]),
    '9': ([0, 1, 2], [32, 4, 5]),
    ':': ([32, 32, 32], [32, 32, 32]),  # Colon rendered as spaces for now; will use putchar
}

def init_cgram(lcd):
    """Load all 6 custom characters into CGRAM on startup."""
    for slot, charmap in CGRAM_CHARS.items():
        lcd.lcd.custom_char(slot, charmap)

def render_big_digit(lcd, digit, col, show=True):
    """
    Render a single big digit (3 cols wide, 2 rows tall) at position (col, 0).
    - digit: '0'-'9', ':', or ' '
    - col: starting column (0-based, 0-17 for 3-col digits on 20-char display)
    - show: if False, render spaces instead (used for hiding chars)
    """
    if not show or digit == ':':
        # Colon is handled separately, render as space
        lcd.lcd.move_to(col, 0)
        lcd.lcd.putstr("   ")
        lcd.lcd.move_to(col, 1)
        lcd.lcd.putstr("   ")
        return

    if digit not in DIGIT_MAP:
        # Unknown char, render as space
        lcd.lcd.move_to(col, 0)
        lcd.lcd.putstr("   ")
        lcd.lcd.move_to(col, 1)
        lcd.lcd.putstr("   ")
        return

    top, bottom = DIGIT_MAP[digit]

    # Render top row
    lcd.lcd.move_to(col, 0)
    for char_slot in top:
        if char_slot == 32:
            lcd.lcd.putstr(" ")
        elif char_slot == 255:
            lcd.lcd.putchar(chr(255))
        else:
            lcd.lcd.putchar(chr(char_slot))

    # Render bottom row
    lcd.lcd.move_to(col, 1)
    for char_slot in bottom:
        if char_slot == 32:
            lcd.lcd.putstr(" ")
        elif char_slot == 255:
            lcd.lcd.putchar(chr(255))
        else:
            lcd.lcd.putchar(chr(char_slot))

def render_colon(lcd, col, visible=True):
    """Render blinking colon at column col between the two rows."""
    if visible:
        lcd.lcd.move_to(col, 0)
        lcd.lcd.putstr(":")
        lcd.lcd.move_to(col, 1)
        lcd.lcd.putstr(":")
    else:
        lcd.lcd.move_to(col, 0)
        lcd.lcd.putstr(" ")
        lcd.lcd.move_to(col, 1)
        lcd.lcd.putstr(" ")

def format_date():
    """Return formatted date string centered for row 2."""
    now = datetime.now()
    date_str = now.strftime("%a  %d %b %Y")  # e.g. "Mon  10 May 2026"
    return date_str.center(20)

def read_weather():
    """Read weather from /tmp/timepi_weather.json, return one-line summary or empty."""
    try:
        with open("/tmp/timepi_weather.json", "r") as f:
            data = json.load(f)
            # Expected format: {"temp": 24, "condition": "Clear", "humidity": 65}
            condition = data.get("condition", "")
            return condition[:20]  # Truncate to 20 chars max
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return ""

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    # Initialize CGRAM with custom characters
    init_cgram(lcd)

    # Clear and set up the display
    lcd.clear()

    last_second = None
    colon_visible = True
    last_colon_toggle = time.time()

    try:
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")  # 24-hour for internal logic
            current_second = now.second

            # --- Update big-digit time on rows 0-1 (HH:MM) ---
            # Check if second changed to avoid redundant redraws
            if current_second != last_second:
                last_second = current_second

                # Extract HH and MM
                hh = now.strftime("%H")
                mm = now.strftime("%M")

                # Render HH (cols 0-2, 3-5)
                render_big_digit(lcd, hh[0], 0)
                render_big_digit(lcd, hh[1], 3)

                # Render colon (col 6)
                render_colon(lcd, 6, visible=True)

                # Render MM (cols 7-9, 10-12)
                render_big_digit(lcd, mm[0], 7)
                render_big_digit(lcd, mm[1], 10)

                # Render SS as small text on the right (cols 14-19)
                ss = now.strftime("%S")
                lcd.lcd.move_to(14, 0)
                lcd.lcd.putstr("  SS")
                lcd.lcd.move_to(14, 1)
                lcd.lcd.putstr(" " + ss)

            # --- Blink colon every 500ms ---
            now_ms = time.time()
            if now_ms - last_colon_toggle >= 0.5:
                colon_visible = not colon_visible
                render_colon(lcd, 6, visible=colon_visible)
                last_colon_toggle = now_ms

            # --- Update date on row 2 ---
            date_str = format_date()
            lcd.write(date_str, line=2)

            # --- Update weather on row 3 ---
            weather = read_weather()
            if weather:
                lcd.write(f"🌡 {weather}".ljust(20), line=3)
            else:
                lcd.write("".ljust(20), line=3)

            # --- Check for exit ---
            if rotary.read_button():
                raise KeyboardInterrupt

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
