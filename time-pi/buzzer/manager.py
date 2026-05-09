import RPi.GPIO as GPIO
import time
import atexit


class Buzzer:
    BUZZER_PIN = 22

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(self.BUZZER_PIN, 1)
        self.pwm.stop()
        atexit.register(self.cleanup)

    def buzz(self, frequency: int, duration: float):
        if frequency <= 0 or duration <= 0:
            return
        self.pwm.ChangeFrequency(frequency)
        self.pwm.start(50)
        time.sleep(duration)
        self.pwm.stop()

    def beep(self):
        self.buzz(1000, 0.1)

    def alarm_beep(self, count: int = 3, delay: float = 0.3):
        for _ in range(count):
            self.beep()
            time.sleep(delay)

    def cleanup(self):
        try:
            self.pwm.stop()
            GPIO.cleanup(self.BUZZER_PIN)
        except Exception:
            pass


if __name__ == "__main__":
    buzzer = Buzzer()
    buzzer.alarm_beep()
    time.sleep(1)
