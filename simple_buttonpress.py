from machine import Pin
import time
import binascii
from shift_register import Output_595, Input_165


class Keypad:
    def __init__(self, nE, S):
        self.nE = Pin(nE, Pin.OUT, value=1)
        self.S = [Pin(s, Pin.OUT, value=0) for s in S]
        

    def press(self, button, delay=1):
        binary = binascii.a2b_base64("AAA" + button)[-1]
        values = [int(d) for d in f'{binary:06b}'][::-1]
        for pin, v in zip(self.S, values):
            pin.value(v)
        self.nE.off()
        time.sleep(0.05)
        self.nE.on()



if __name__ == "__main__":
    kp = Keypad(nE=0, S=[5, 6, 7, 20, 21, 22])
    kp.press("4")
