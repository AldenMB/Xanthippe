import gpiozero
import time

default_pins = {
    "led": 13,
    "e": 14,
    "rs": 15,
    "d4": 16,
    "d5": 17,
    "d6": 18,
    "d7": 19,
}


class LCD:
    """
    Minimal driver for HD44780 character display.
    backlight pin is connected to a transistor, which turns
    the backlight on when high
    """
    def __init__(self, pins=default_pins):
        self.backlight = gpiozero.PWMLED(pins["led"])
        self.data = [
            gpiozero.DigitalOutputDevice(pins[p]) for p in "d4 d5 d6 d7".split()
        ]
        self.clock = gpiozero.DigitalOutputDevice(pins["e"])
        self.select = gpiozero.DigitalOutputDevice(pins["rs"])

        # configuration
        self.select.off()
        for byte in [
            0x33,  # 8 bit interface
            0x32,  # 8 bit interface
            0x28,  # 4 bit interface, 2 display lines, 8px font
            0x0C,  # display on, cursor off, blinking off
            0x06,  # left-to-right mode
        ]:
            self.send_byte(byte)
        self.clear()
        self.backlight.value = 0.1

    def clear(self):
        self.select.off()
        self.send_byte(0x01)
        return self

    def goto_line(self, line):
        self.select.off()
        self.send_byte(0x80 if line == 0 else 0xC0)
        return self

    def clockpulse(self):
        """
        The sleep constants were determined empirically.
        The data is sent on a falling edge, so we only
        need a buffer around that.
        """
        self.clock.on()
        time.sleep(0.0005)
        self.clock.off()
        time.sleep(0.0005)
        return self

    def write(self, message, line=None):
        if line is not None:
            self.goto_line(line)
        self.select.on()
        for char in message:
            self.send_byte(ord(char))
        return self

    def send_byte(self, byte):
        lo = byte & 0xF
        hi = byte >> 4

        for nibble in hi, lo:
            for i, pin in enumerate(self.data):
                pin.value = 1 & (nibble >> i)
            self.clockpulse()


if __name__ == "__main__":
    lcd = LCD()
    lcd.write("This is a test")
    lcd.write("of the LCD scrn.", line=1)
    time.sleep(1)
