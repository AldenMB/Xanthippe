import rp2

@rp2.asm_pio(fifo_join = PIO.JOIN_RX, sideset_init=(PIO.OUT_LOW,PIO.OUT_LOW))
def shift_in_lcd():
"""
Pins:
    In:
        0 - register data
        1 - first timing trigger (#3)
        2 - second timing trigger (#2)
    Sideset:
        0 - register clock
        1 - register hold

scratch variables:
x - which bit am I shifting in?
  - which line do I jump to?
y - which backplane am I shifting from?
"""    
    label("wait_0")
    set(y, 3)
    wait(1, pin, 1)
    jmp("shift")
    
    label("wait_3")
    set(y, 2)
    wait(0, pin, 1)
    jmp("shift")
    
    label("wait_2")
    set(y, 1)
    wait(1, pin, 2)
    jmp("shift")
    
    label("wait_1")
    set(y, 0)
    wait(0, pin, 2)
    jmp("shift")
    
    label("shift")
    set(x, 31).side(0b10)
    label("shift_loop")
    in(pins, 1).side(0b11)
    jmp(x_dec, "shift_loop").side(0b10)
    push(noblock).side(0b00)
    mov(y, x)
    jmp(x_dec, "wait_0")
    jmp(x_dec, "wait_1")
    jmp(x_dec, "wait_2")
    jmp(x_dec, "wait_3")
    