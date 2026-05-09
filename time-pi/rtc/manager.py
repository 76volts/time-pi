from datetime import datetime
import atexit


class RTCManager:
    """
    Kernel-based RTC manager that wraps system time.
    Assumes system clock is synced with the hardware RTC by the OS.
    """

    def __init__(self):
        atexit.register(self.cleanup)

    def read_datetime(self) -> datetime:
        return datetime.now()

    def set_datetime(self, dt: datetime):
        pass  # Setting time is delegated to the OS

    def cleanup(self):
        pass


if __name__ == "__main__":
    rtc = RTCManager()
    now = rtc.read_datetime()
    print("System time:", now.strftime("%Y-%m-%d %H:%M:%S"))
