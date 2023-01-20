import binascii
import gpiozero
import time


class ButtonPresser:
    def __init__(self):
        self.power = gpiozero.OutputDevice(20, initial_value=True)
        self.enable = gpiozero.DigitalOutputDevice(
            21, active_high=False, initial_value=False
        )
        self.data = [gpiozero.OutputDevice(i) for i in range(22, 28)]

    def send(self, symbol):
        binary = binascii.a2b_base64("AAA" + symbol)[-1]
        values = (int(d) for d in f"{binary:06b}"[::-1])
        for pin, value in zip(self.data, values):
            pin.value = value
        self.enable.blink(on_time=0.05, off_time=0.1, n=1, background=False)
        if symbol == "3":
            # reset takes additional time for some reason
            time.sleep(0.35)


if __name__ == "__main__":
    bp = ButtonPresser()
