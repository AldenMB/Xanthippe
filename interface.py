import rp2


@rp2.asm_pio(fifo_join=PIO.JOIN_RX, sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW))
def shift_in_lcd():
    """
    This pulls in data from the 74HC165 shift registers which are connected to the
    LCD, clocked on the outputs form two of the ground planes. The correspondence
    to the 74HC165 pins is as follows:
    data - Q7
    clock - CP
    nsample - ~PL

    The data changes on the rising edge of the clock. nsample goes on a low pulse,
    and must be kept high during shifting.

    The worst-case propagation  delay from the 74HC165 is 250ns, which means that
    we can safely read data off at a rate of 4 MHz without any trouble. Of course,
    the Pico runs at 125 MHz by default, so it would be better to divide that evenly
    by 32 to get 3_906_250 Hz.

    Doing it this way, it takes (2cycles/bit)*(250ns/cycle)*(32bits) = 16us to read
    all the bits. That is significantly faster than the 3ms clock which the TI-30Xa
    uses for its LCD driver. We should have no trouble at all acquiring all the bits
    in time, in fact we could afford to go much slower if we wish.

    Pins:
        In:
            0 - data
            1 - first timing trigger (#3)
            2 - second timing trigger (#2)
        Sideset:
            0 - clock
            1 - nsample

    scratch variables:
    x - which bit am I shifting in?
    """
    clock = 0b01
    nsample = 0b10
    loop_number = 0
    for trigger_pin, condition in [(1, 1), (1, 0), (2, 1), (2, 0)]:
        wait(condition, pin, trigger_pin)

        set(x, 31).side(nsample | 0)
        label(loop_number)
        in_(pins, 1).side(nsample | clock)
        jmp(x_dec, loop_number).side(nsample | 0)
        push(noblock).side(0 | 0)
        loop_number += 1

    irq(rel(0))


@rp2.asm_pio(
    set_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_HIGH),
    sideset_init=(PIO.OUT_LOW),
    pull_thresh=16,
    fifo_join=PIO.JOIN_TX,
)
def shift_out_button():
    """
    This drives the 74HC595 shift registers on the Xanthippe adapter board.

    Here is a translation between my pin names and the 74HC595:
    data - SER
    clock - SRCLK
    ~blank - ~SRCLR
    show - RCLK

    The 74HC595 would prefer to receive its inputs no faster than 4 MHz,
    though it can be persuaded to go faster, either by increasing its voltage
    or by carefully manipulating the timing between transitions.
    The Pico runs at 125MHz by default, so a 32x clock division will bring it
    down to 3.9 MHz, well within the safety realm. The exact frequency is
    3_906_250 Hz, so that's what to give StateMachine.init().

    It's unclear how long a button has to be pressed in order to register reliably.
    We will have to experiment to see. We still have both scratch variables
    and four of the delay bits, so we should have no trouble introducing whatever
    delay is needed here.
    
    For now, a delay of 0.1 seconds is made by introducing a delay of 5**8=390625 cycles.
    That should be much more than enough.

    Pins:
        In:
            0 - data
            1 - show
            2 - ~blank
        Sideset:
            0 - clock
    """
    show = 0b010
    noblank = 0b100
    # tell the calculator to release the buttons
    set(pins, 0 | 0)  # empty the register
    set(pins, show | noblank)  # show the result
    set(pins, 0 | noblank)

    # shift out the latest button press
    pull(block)
    label("bitloop")
    out(pins, 1).side(0)
    jmp(not_osre, "bitloop").side(1)

    # show the button press
    set(pins, show | noblank)

    # TODO: figure out the amount of time to keep the button pressed
    
    set(y, 31)
    label('delayloop')
    set(x, 31)[15]
    label('delayloop2') 
    nop[15]
    nop[15]
    nop[15]
    jmp(x_dec, 'delayloop2')[15]
    jmp(y_dec, 'delayloop')[15]
