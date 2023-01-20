from driver.display import LCD
from driver.buttonpresser import ButtonPresser
from driver.lcdreader import LCDReader
import json
from dataclasses import dataclass

with open("button_codes.json") as f:
    BUTTON_CODES = json.load(f)

BUTTON_NAMES = {val: key for key, val in BUTTON_CODES.items()}


class SevenSegment(int):
    """
     -A-
    |   |
    F   B
    |   |
     -G-
    |   |
    E   C
    |   |
     -D- DP
    """

    def dp(self):
        return self & 0x80

    def __str__(self):
        """
        >>> str(SevenSegment(0x63))
        '4 '
        >>> str(SevenSegment(0x7a))
        '3 '
        >>> str(SevenSegment(0xe3))
        '4.'
        >>> str(SevenSegment(0b000011))
        Traceback (most recent call last):
        ...
        ValueError: no symbol for bitmap 00000011
        """
        dp = "." if self.dp() else " "
        try:
            return {
                ##cbadegf
                0b0000000: " ",
                0b1100000: "1",
                0b0111110: "2",
                0b1111010: "3",
                0b1100011: "4",
                0b1011011: "5",
                0b1011111: "6",
                0b1110001: "7",
                0b1111111: "8",
                0b1111011: "9",
                0b1111101: "0",
                0b0011111: "E",
                0b0000110: "r",
                0b1001110: "o",
                0b0001111: "t",
                0b1110111: "A",
                0b0001000: "_",
                0b0001010: "=",
                0b1001000: "/",
                0b0100001: '"',
                0b0000001: "'",
                0b1000110: "n",
                0b0000010: "-",
            }[self & 0x7F] + dp
        except KeyError:
            raise ValueError(f"no symbol for bitmap {self:08b}")


def unpack(byte):
    return (bool(int(c)) for c in f"{byte:08b}")


class Screen(bytes):
    def __str__(self):
        r"""
        >>> print(Screen(b'\xff'*14))
        M1 M2 M3 2nd HYP SCIENG FIX STAT DEGRAD XR () K
        -8.8.8.8.8.8.8.8.8.8. -88
        >>> print(Screen(b'`\x00\x00cz\x00\x00\x00\x00\x00\x00\x00\x00\x00')) # doctest: +NORMALIZE_WHITESPACE
                                         DEG
                         3 4
        """
        s = {}
        (
            s["STAT "],
            s["DE"],
            s["G"],
            s["FIX "],
            s["R "],
            s["X"],
            s["RAD "],
            e2g,
        ) = unpack(self[0])
        exponent = [SevenSegment(x) for x in self[1:3]]
        s["K"] = exponent[0].dp()
        s["() "] = exponent[1].dp()
        mantissa = [SevenSegment(x) for x in self[3:13]]
        (
            s["M3 "],
            g10,
            s["M2 "],
            s["M1 "],
            s["2nd "],
            s["HYP "],
            s["ENG "],
            s["SCI"],
        ) = unpack(self[13])

        row1 = "".join(
            x if s[x] else " " * len(x)
            for x in "M1 |M2 |M3 |2nd |HYP |SCI|ENG |FIX |STAT |DE|G|RAD |X|R |() |K".split(
                "|"
            )
        )

        row2 = (
            ("-" if g10 else " ")
            + "".join(str(seg) for seg in mantissa[::-1])
            + (" -" if e2g else "  ")
            + "".join(str(seg)[0] for seg in exponent[::-1])
        )
        return f"{row1}\n{row2}"


class Calculator:
    def __init__(self):
        self.display = LCD()
        self.reader = LCDReader()
        self.presser = ButtonPresser()

    def interactive(self):
        print(Screen(self.reader.showing()))
        while (b := input("press> ").strip()) in BUTTON_CODES:
            code = BUTTON_CODES[b]
            msg = f"Pressed {b:<6}#{code}"
            print(msg)
            self.display.write(msg, line=0)
            msg = "waiting...".ljust(16)
            print(msg)
            self.display.write(msg, line=1)

            self.presser.send(code)

            showing = self.reader.showing()
            print(showing.hex(" "))
            hex = showing.hex()
            self.display.write(f"{code} {hex[:14]}", line=0)
            self.display.write(f"  {hex[14:]}", line=1)
            print(msg)
            print(Screen(showing))


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    c = Calculator()
    c.interactive()