import time
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lcd")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rotary")))

from lcd.manager import LCDManager
from rotary.manager import RotaryEncoder

# Pomodoro constants
DEFAULT_WORK_MINUTES = 25
DEFAULT_BREAK_MINUTES = 5
MIN_WORK_MINUTES = 15
MAX_WORK_MINUTES = 60
ADJUST_STEP = 5

# State machine
STATE_IDLE = 0
STATE_RUNNING_WORK = 1
STATE_PAUSED_WORK = 2
STATE_RUNNING_BREAK = 3
STATE_PAUSED_BREAK = 4
STATE_EXPIRED = 5

def format_mm_ss(total_seconds):
    """Convert seconds to 'MM:SS' format."""
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def display_idle(lcd, work_minutes):
    """Display idle state with pomodoro count."""
    lcd.clear()
    lcd.write("Pomodoro 1".center(20), line=0)
    lcd.write("".ljust(20), line=1)
    
    # Display duration as large-ish text on lines 2-3
    duration_str = f"{work_minutes}:00"
    lcd.write(duration_str.center(20), line=2)
    lcd.write("Press to start".center(20), line=3)

def display_running_work(lcd, remaining_seconds, work_minutes, pomodoro_count):
    """Display running work timer."""
    lcd.clear()
    lcd.write(f"Pomodoro {pomodoro_count}".center(20), line=0)
    lcd.write("WORK".center(20), line=1)
    
    time_str = format_mm_ss(remaining_seconds)
    lcd.write(time_str.center(20), line=2)
    lcd.write("Press to pause".center(20), line=3)

def display_paused_work(lcd, remaining_seconds, work_minutes, pomodoro_count):
    """Display paused work timer."""
    lcd.clear()
    lcd.write(f"Pomodoro {pomodoro_count}".center(20), line=0)
    lcd.write("PAUSED (work)".center(20), line=1)
    
    time_str = format_mm_ss(remaining_seconds)
    lcd.write(time_str.center(20), line=2)
    lcd.write("Rotate: adjust".center(20), line=3)

def display_running_break(lcd, remaining_seconds, break_minutes):
    """Display running break timer."""
    lcd.clear()
    lcd.write("Break Time!".center(20), line=0)
    lcd.write("BREAK".center(20), line=1)
    
    time_str = format_mm_ss(remaining_seconds)
    lcd.write(time_str.center(20), line=2)
    lcd.write("Press to pause".center(20), line=3)

def display_paused_break(lcd, remaining_seconds, break_minutes):
    """Display paused break timer."""
    lcd.clear()
    lcd.write("Break Time!".center(20), line=0)
    lcd.write("PAUSED (break)".center(20), line=1)
    
    time_str = format_mm_ss(remaining_seconds)
    lcd.write(time_str.center(20), line=2)
    lcd.write("Press to resume".center(20), line=3)

def display_expired(lcd, expired_type, pomodoro_count):
    """Display timer expired screen."""
    lcd.clear()
    if expired_type == "work":
        lcd.write("Work Time Over!".center(20), line=0)
        lcd.write("Pomodoro " + str(pomodoro_count), line=1)
    else:
        lcd.write("Break Time Over!".center(20), line=0)
        lcd.write("Ready to work?".center(20), line=1)
    
    lcd.write("Press to continue".center(20), line=2)
    lcd.write("Hold 2s to reset".center(20), line=3)

def main():
    lcd = LCDManager()
    rotary = RotaryEncoder()

    # State variables
    state = STATE_IDLE
    work_minutes = DEFAULT_WORK_MINUTES
    break_minutes = DEFAULT_BREAK_MINUTES
    pomodoro_count = 1
    
    remaining_seconds = work_minutes * 60
    start_time = None
    paused_time = None
    
    hold_start = None
    HOLD_THRESHOLD = 2.0  # seconds to hold for reset

    try:
        while True:
            now = time.time()
            
            # --- IDLE STATE ---
            if state == STATE_IDLE:
                display_idle(lcd, work_minutes)
                
                if rotary.read_button():
                    state = STATE_RUNNING_WORK
                    start_time = time.time()
                    remaining_seconds = work_minutes * 60
                
                # Rotation in idle: adjust work duration
                pos = rotary.read_position()
                if pos > 0:
                    work_minutes = min(work_minutes + ADJUST_STEP, MAX_WORK_MINUTES)
                    rotary.reset_position()
                elif pos < 0:
                    work_minutes = max(work_minutes - ADJUST_STEP, MIN_WORK_MINUTES)
                    rotary.reset_position()

            # --- RUNNING WORK STATE ---
            elif state == STATE_RUNNING_WORK:
                elapsed = time.time() - start_time
                remaining_seconds = max(0, (work_minutes * 60) - elapsed)
                
                display_running_work(lcd, int(remaining_seconds), work_minutes, pomodoro_count)
                
                if rotary.read_button():
                    state = STATE_PAUSED_WORK
                    paused_time = time.time()
                    hold_start = None
                
                if remaining_seconds <= 0:
                    state = STATE_EXPIRED
                    paused_time = time.time()

            # --- PAUSED WORK STATE ---
            elif state == STATE_PAUSED_WORK:
                display_paused_work(lcd, int(remaining_seconds), work_minutes, pomodoro_count)
                
                # Check for button press (resume)
                if rotary.read_button():
                    state = STATE_RUNNING_WORK
                    start_time = time.time() - (work_minutes * 60 - remaining_seconds)
                    hold_start = None
                
                # Check for long hold (reset)
                if hold_start is None:
                    hold_start = time.time()
                elif time.time() - hold_start >= HOLD_THRESHOLD:
                    state = STATE_IDLE
                    remaining_seconds = work_minutes * 60
                    paused_time = None
                    hold_start = None
                
                # Rotation: adjust work duration
                pos = rotary.read_position()
                if pos > 0:
                    work_minutes = min(work_minutes + ADJUST_STEP, MAX_WORK_MINUTES)
                    rotary.reset_position()
                elif pos < 0:
                    work_minutes = max(work_minutes - ADJUST_STEP, MIN_WORK_MINUTES)
                    rotary.reset_position()

            # --- RUNNING BREAK STATE ---
            elif state == STATE_RUNNING_BREAK:
                elapsed = time.time() - start_time
                remaining_seconds = max(0, (break_minutes * 60) - elapsed)
                
                display_running_break(lcd, int(remaining_seconds), break_minutes)
                
                if rotary.read_button():
                    state = STATE_PAUSED_BREAK
                    paused_time = time.time()
                    hold_start = None
                
                if remaining_seconds <= 0:
                    state = STATE_EXPIRED
                    paused_time = time.time()

            # --- PAUSED BREAK STATE ---
            elif state == STATE_PAUSED_BREAK:
                display_paused_break(lcd, int(remaining_seconds), break_minutes)
                
                if rotary.read_button():
                    state = STATE_RUNNING_BREAK
                    start_time = time.time() - (break_minutes * 60 - remaining_seconds)
                    hold_start = None

            # --- EXPIRED STATE ---
            elif state == STATE_EXPIRED:
                # Determine which timer expired
                if remaining_seconds <= 0:
                    if paused_time is None:
                        paused_time = time.time()
                    
                    # Figure out what expired
                    if state == STATE_EXPIRED:
                        # We just transitioned here; check if it was work or break
                        # For simplicity, we'll track it separately
                        pass
                
                # Show expired screen
                if remaining_seconds > (break_minutes * 60) / 2:
                    # Work timer expired
                    display_expired(lcd, "work", pomodoro_count)
                else:
                    # Break timer expired
                    display_expired(lcd, "break", pomodoro_count)
                
                if rotary.read_button():
                    if remaining_seconds > (break_minutes * 60) / 2:
                        # Work expired -> start break
                        state = STATE_RUNNING_BREAK
                        start_time = time.time()
                        remaining_seconds = break_minutes * 60
                        paused_time = None
                    else:
                        # Break expired -> increment count, go to idle
                        pomodoro_count += 1
                        state = STATE_IDLE
                        remaining_seconds = work_minutes * 60
                        paused_time = None
                    hold_start = None
                
                # Check for long hold to reset
                if hold_start is None:
                    hold_start = time.time()
                elif time.time() - hold_start >= HOLD_THRESHOLD:
                    state = STATE_IDLE
                    pomodoro_count = 1
                    remaining_seconds = work_minutes * 60
                    paused_time = None
                    hold_start = None

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        rotary.cleanup()

if __name__ == "__main__":
    main()
