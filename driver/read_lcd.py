import gpiozero
import time


def regroup_reading_bits(partial_readings):
    data = bytearray(14)
    for reading_number, (timestamp, reading) in enumerate(partial_readings):
        for i in range(14):
            data[i] |= reading

class LCDReader:
    def __init__(self):
        self.sample = gpiozero.OutputDevice(0, active_high = False, initial_value = False)
        self.clock = gpiozero.OutputDevice(1)
        self.data = gpiozero.InputDevice(2, pull_up = True)
        self.triggers = [
            gpiozero.DigitalInputDevice(i, pull_up = True) for i in range(6, 2, -1)
        ]
        for i, trig in enumerate(self.triggers):
            def interrupt(*args, i=i):
                self.on_interrupt(i)
            trig.when_deactivated = interrupt
        
        self.partial_readings = []
        self.reading_log = []
        
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
            self.reading_log.append(self.partial_readings)
            self.partial_readings = []        
            
        
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
    
    bp.send('3') # reset
    time.sleep(0.5)
    bp.send('4') # on
    time.sleep(0.15)
    bp.send('b') # 3
    time.sleep(0.15)
    bp.send('j') # 4
    time.sleep(0.15)
    
    reader = LCDReader()
    time.sleep(0.5)
    
    print(f'{len(reader.reading_log)=}')
    distinct = set(tuple(list(zip(*entry))[1]) for entry in reader.reading_log)
    result = '\n'.join(f'{x:032b}' for dd in distinct for x in dd)
    print(result)
    assert result == '''00000000010000000000000000000111
10000010100000000000000000001011
10000011110000000000000000001101
00000001100000000000000000001110'''
    
    
    