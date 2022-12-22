from machine import Pin
import time
import binascii
from shift_register import Output_595, Input_165


class Keypad(Output_595):
    def __init__(self, show, clock, nblank, data):
        super().__init__(show, nblank, clock, data, 2)

    def press(self, button, delay=1):
        binary = binascii.a2b_base64("AAA" + button)[-1]
        A = 1 << (binary & 7)
        B = 1 << (((binary >> 3) & 7) | 8)
        to_write = A | B
        print(f"7654321076543210\n{to_write:016b}")
        self.shift_bytes(to_write)
        self.show()
        if delay:
            time.sleep(delay)
        self.clear()
        self.show()


class LCD(Input_165):
    def __init__(self, nsample, clock, data, plane_a, plane_c):
        super().__init__(nsample, clock, data, 4)
        self.plane_a = Pin(plane_a, Pin.IN)
        self.plane_c = Pin(plane_c, Pin.IN)

    def read(self):
        bits = super().read()
        corrected = bits ^ ((1 << 32) - (1 << 4))
        return corrected


if __name__ == "__main__":
    kp = Keypad(show=18, clock=17, nblank=19, data=16)
    lcd = LCD(nsample=9, clock=11, data=10, plane_a=8, plane_c=12)
    kp.press("4")


    header = "   33322222222221111111111000000000\n   21098765432109876543210987654321"
    while True:

        while not lcd.plane_a.value():
            pass
        while (A:=lcd.read()) & 15 != 8:
            pass
        while lcd.plane_a.value():
            pass
        while (B:=lcd.read()) & 15 != 4:
            pass
        while not lcd.plane_c.value():
            pass
        while (C:=lcd.read()) & 15 != 2:
            pass
        while lcd.plane_c.value():
            pass
        while (D:=lcd.read()) & 15 != 1:
            pass
        
        
        message = '\n'.join(f'{letter}: {value:032b}' for letter, value in zip('ABCD', [A, B, C, D]))
        message = message.replace("0", ".").replace("1", "#")
        print(header)
        print(message)
        time.sleep(0.25)
