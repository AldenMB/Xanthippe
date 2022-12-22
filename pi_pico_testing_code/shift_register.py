from machine import Pin
import time


class Output_595:
    """
    Micropython interface for the '595 shift registers.
    I do not implement the OE pin because I do not use it.
    Similarly I don't support shifting partial bytes.
    """

    def __init__(self, RCLK, nSRCLR, SRCLK, SER, number_of_bytes=1):
        self.bit_count = 8 * number_of_bytes
        self.RCLK = Pin(RCLK, Pin.OUT, value=0)
        self.nSRCLR = Pin(nSRCLR, Pin.OUT, value=0)
        self.SRCLK = Pin(SRCLK, Pin.OUT, value=0)
        self.SER = Pin(SER, Pin.OUT, value=0)

        # ensure the shift register starts in a stable state
        self.clear()
        self.show()

    def clear(self):
        self.nSRCLR.off()  # set by low state
        self.nSRCLR.on()

    def show(self):
        self.RCLK.on()  # set by rising edge
        self.RCLK.off()

    def shift_bytes(self, b):
        for i in range(self.bit_count - 1, -1, -1):
            self.SER.value(1 & (b >> i))
            self.SRCLK.on()  # set by rising edge
            self.SRCLK.off()


class Input_165:
    """
    Micropython interface for the '165 shift registers.
    I have not included an interface for CE, because I do not need it.
    """

    def __init__(self, nPL, CP, Q7, number_of_bytes):
        self.bit_count = 8 * number_of_bytes
        self.nPL = Pin(nPL, Pin.OUT, value=0)
        self.CP = Pin(CP, Pin.OUT, value=0)  # rising edge triggered
        self.Q7 = Pin(Q7, Pin.IN)

    def read(self):
        output = 0
        self.nPL.on()
        for i in range(self.bit_count - 1, -1, -1):
            output |= self.Q7.value() << i
            self.CP.on()
            self.CP.off()
        self.nPL.off()
        return output
