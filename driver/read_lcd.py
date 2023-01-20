import gpiozero
import time
from dataclasses import dataclass


LCD_REFRESH_PERIOD = 24_000_000  # milliseconds -> nanoseconds


def normalize_reading(bits):
    """
    Pack the raw bits into one byte per segment. Discard the checksum.
    
    example:
    >>> normalize_reading([0b00000000010000000000000000000111,\
                           0b10000010100000000000000000001011,\
                           0b10000011110000000000000000001101,\
                           0b00000001100000000000000000001110]).hex(' ')
    '60 00 00 63 7a 00 00 00 00 00 00 00 00 00'
    """
    rows = [f"{x>>4:028b}" for x in bits]
    columns = zip(*rows)
    paired = zip(*[iter(columns)] * 2)
    return bytes(int("".join(a + b), base=2) for a, b in paired)


@dataclass
class LogEntry:
    """one thing that has been shown on screen"""

    shown: int
    start: int
    end: int = None

    def __post_init__(self):
        if self.end is None:
            self.end = self.start


class LCDReader:
    def __init__(self):
        self.sample = gpiozero.OutputDevice(0, active_high=False, initial_value=False)
        self.clock = gpiozero.OutputDevice(1)
        self.data = gpiozero.InputDevice(2, pull_up=True)
        self.triggers = [
            gpiozero.DigitalInputDevice(i, pull_up=True) for i in range(6, 2, -1)
        ]
        for i, trig in enumerate(self.triggers):

            def interrupt(*args, i=i):
                self.on_interrupt(i)

            trig.when_deactivated = interrupt

        self.partial_readings = []
        self.log = []

    def on_interrupt(self, i):
        now = time.monotonic_ns()
        if i == 0:
            self.partial_readings = []
        else:
            if len(self.partial_readings) != i:
                self.partial_readings = []
                return
            then = self.partial_readings[-1][0]
            if now - then > 6_000_000:
                self.partial_readings = []
                return

        partial = self.acquire()
        checksum = 15 & ~partial
        if checksum != 8 >> i:
            return

        self.partial_readings.append((now, partial))
        if i == 3:
            self.record()
            self.partial_readings = []

    def record(self):
        (time, *_), bits = zip(*self.partial_readings)
        showing = normalize_reading(bits)
        if (
            self.log
            and self.log[-1].shown == showing
            and time - self.log[-1].end < 1.5 * LCD_REFRESH_PERIOD
        ):
            self.log[-1].end = time
        else:
            self.log.append(LogEntry(showing, time))

    def acquire(self):
        result = 0
        self.sample.off()
        for i in range(31, -1, -1):
            result |= self.data.value << i
            self.clock.off()
            self.clock.on()
        self.sample.on()
        return result


if __name__ == "__main__":
    from buttonpress import ButtonPresser

    bp = ButtonPresser()

    bp.send("3")  # reset
    bp.send("4")  # on
    bp.send("b")  # 3
    bp.send("j")  # 4

    reader = LCDReader()
    time.sleep(0.5)

    print(f"{len(reader.log)=}")
    print(f"{reader.log=}")

    for entry in reader.log:
        print(entry.shown.hex(" "))
        print(f"start={entry.start}")
        print(f"duration={entry.end-entry.start}")
