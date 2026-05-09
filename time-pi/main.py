# main.py
import time
import datetime
from rotary import manager as rotary
from lcd import manager as lcd

# Import screen modules
import home
import quotes

# List of screen functions to cycle through
screens = [home.display_home, quotes.display_quotes]
current_screen_index = 0

def switch_screen(delta):
    global current_screen_index
    current_screen_index = (current_screen_index + delta) % len(screens)
    screens[current_screen_index]()  # Call the corresponding display function

def is_night_time():
    now = datetime.datetime.now()
    return now.hour >= 22 or now.hour < 6  # Night is from 10 PM to 6 AM

if __name__ == "__main__":
    lcd.initialize()
    rotary.initialize()

    last_clk_state = rotary.get_clk()

    while True:
        clk_state = rotary.get_clk()

        if clk_state != last_clk_state:
            if rotary.get_dt() != clk_state:
                switch_screen(1)  # Clockwise
            else:
                switch_screen(-1)  # Counter-clockwise
            time.sleep(0.25)  # debounce
            last_clk_state = clk_state

        if is_night_time():
            lcd.backlight_off()
        else:
            lcd.backlight_on()

        time.sleep(0.1)
